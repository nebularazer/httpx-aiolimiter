import asyncio
from typing import Union
from time import monotonic
from typing import AsyncContextManager

from aiolimiter import AsyncLimiter
from httpx import AsyncClient
from aiohttp import ClientSession

ref = monotonic()

class anullcontext:
    async def __aenter__(self):
        return None
    async def __aexit__(self, *excinfo):
        return None

async def task(
    x: int,
    limiter: AsyncLimiter,
    sema: AsyncContextManager,
    client: Union[AsyncClient,ClientSession]
):
    async with sema:
        async with limiter:
            resp = await client.get('http://localhost:8000')
            print(f"{monotonic() - ref:.5f}: request")

async def main(num_requests: int, use_sema: bool, rate: float = 20, period: float = 1, use_aiohttp: bool = False):
    limiter = AsyncLimiter(rate, period)
    sema = asyncio.BoundedSemaphore(100) if use_sema else anullcontext()

    if use_aiohttp:
        client = ClientSession()
    else:
        client = AsyncClient()

    tasks = [
        asyncio.create_task(task(x, limiter, sema, client))
        for x in range(num_requests)
    ]

    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='use_sema', action='store_true', help='Use a bounded semaphore')
    parser.add_argument(
        '-r', dest='rate', type=float, default=20, help='Maximum number of requests in a time period'
    )
    parser.add_argument(
        '-p', dest='period', type=float, default=1, help='Rate limit time period'
    )
    parser.add_argument('-u', dest='use_uvloop', action='store_true', help='Use uvloop instead of the default loop')
    parser.add_argument('-a', dest='use_aiohttp', action='store_true', help='Use aiohttp client instead of httpx client')
    parser.add_argument('num_requests', nargs='?', default=50, type=int)
    args = parser.parse_args()
    if args.use_uvloop:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main(args.num_requests, args.use_sema, args.rate, args.period, args.use_aiohttp))
