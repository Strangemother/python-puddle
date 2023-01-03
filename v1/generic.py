import asyncio

def async_head(promise_set, pipe=None):
    promise, *args = promise_set
    asyncio.run(promise(*args))
