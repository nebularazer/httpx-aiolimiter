import asyncio

from random import uniform

from sanic import Sanic
from sanic.response import json

app = Sanic("example")

@app.get("/")
async def hello_world(request):
    time = uniform(0.25, 0.80)
    await asyncio.sleep(time)

    return json({"time": time})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, access_log=True)
