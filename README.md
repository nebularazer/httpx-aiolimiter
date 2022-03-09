# example

Example repository for the discussion at: https://github.com/encode/httpx/discussions/1933

## run server
```
python server.py
```

## run client

without semaphore (this is broken on my machine)
```
python client 10000
# python client 10000 -u (uvloop makes no difference)
```

with semaphore (this works as expected on my machine)
```
python client 10000 -s
```

with aiohttp (this works as expected on my machine)
```
python client 10000 -a
```
