import time

from puddles import raw, extras

def main():
    """In this example we _run_ a single method but without the _wait_.

    To futher expand, we can execute mutiple runs - and choose to apply additional
    futures to wait upon.
    """

    results = raw.run(
        (
            process_func,   # from the above example
            async_process_func,
        )
    )
    # The results are the return values from the sync_sleep
    return results


def sync_sleep(index=-1, **other):
    """Run a method as a raw unit with meta arguments:

        >>> raw.unit(sync_sleep, meta.head, index=meta.index),
        sync_sleep <__mp_main__.ProcessHead object> index 0

    In this example we return the call index of the thread.
    """
    print('sync_sleep', 'index:', index, 'options:', other)
    time.sleep(extras.variate(3, .5))
    return index

def process_func(*a):
    """Same as `raw.run(extras.sync_sleep, 3)`"""
    print('Process execution', *a)
    extras.sync_sleep(3) # not async.
    return 'egg'

async def async_process_func(timeout=3):
    """Same as `raw.run(extras.async_sleep, 3)`"""
    print('Async Process execution', timeout)

    await extras.async_sleep(timeout) # is async.
    return timeout


if __name__ == '__main__':

    res = main()
    print(res)

