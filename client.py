import asyncio
import logging
import math
from typing import AsyncContextManager, Union

from aiolimiter import AsyncLimiter
from aiohttp import ClientSession
from httpx import AsyncClient

logger = logging.getLogger("main")


class TaskNameFilter(logging.Filter):
    def filter(self, record):
        try:
            task = asyncio.current_task()
        except RuntimeError:
            task = None
        record.taskname = task.get_name() if task is not None else "~"
        return True


class anullcontext:
    async def __aenter__(self):
        return None

    async def __aexit__(self, *excinfo):
        return None


async def task(limiter: AsyncLimiter, sema: AsyncContextManager, client: AsyncClient):
    async with sema:
        logger.debug(">> sema")
        async with limiter:
            logger.debug(">> limiter")
            await client.get("http://localhost:8000")
            logger.info("request made")
        logger.debug("<< limiter")
    logger.debug("<< sema")


async def main(
    num_requests: int,
    use_sema: bool,
    rate: float = 20,
    period: float = 1,
    client_factory: type[Union[AsyncClient, ClientSession]] = AsyncClient,
):
    limiter = AsyncLimiter(rate, period)
    sema = asyncio.BoundedSemaphore(100) if use_sema else anullcontext()
    client = client_factory()
    width = 1 + int(math.log10(num_requests))
    tasks = [
        asyncio.create_task(task(limiter, sema, client), name=f"#r{x:0{width}d}")
        for x in range(num_requests)
    ]

    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", dest="use_sema", action="store_true", help="Use a bounded semaphore"
    )
    parser.add_argument("-u", dest="use_uvloop", action="store_true", help="Use uvloop")
    parser.add_argument(
        "-a",
        dest="use_aiohttp",
        action="store_true",
        help="Use aiohttp instead of httpx",
    )
    parser.add_argument(
        "-d",
        dest="debug",
        action="store_true",
        help="Enable asyncio logging and debugging",
    )
    parser.add_argument(
        "-r",
        dest="rate",
        type=float,
        default=20,
        help="Maximum number of requests in a time period",
    )
    parser.add_argument(
        "-p", dest="period", type=float, default=1, help="Rate limit time period"
    )
    parser.add_argument("num_requests", nargs="?", default=50, type=int)
    args = parser.parse_args()

    factory = ClientSession if args.use_aiohttp else AsyncClient

    if args.use_uvloop:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="(%(relativeCreated)06d %(taskname)s) %(levelname)s:%(name)s:%(message)s",
    )
    filter = TaskNameFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(filter)
    logging.info("Running test with %r", args)

    asyncio.run(
        main(
            args.num_requests,
            args.use_sema,
            args.rate,
            args.period,
            client_factory=factory,
        ),
        debug=args.debug,
    )
