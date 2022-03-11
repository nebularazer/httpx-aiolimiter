# example

Example repository for the discussion at: https://github.com/encode/httpx/discussions/1933

## run server
```
python server.py
```

## run client

Problematic run, no semaphore
```
python client.py -d 500
```

With semaphore
```
python client.py -d 500 -s
```

Using aiohttp, no semaphore
```
python client.py -d 500 -a
```

Using aiohttp and semaphore
```
python client.py -d 500 -sa
```
