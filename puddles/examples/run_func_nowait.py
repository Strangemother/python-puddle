import time

from puddles import raw, extras

def main():
    """In this example we _run_ a single method but without the _wait_.

    To futher expand, we can execute mutiple runs - and choose to apply additional
    futures to wait upon.
    """
    futures = raw.run(sync_sleep, 1, foo='bar', wait_futures=False)
    second_futures = raw.run(sync_sleep, 4, foo='seconds', wait_futures=False)
    results = raw.run(sync_sleep, 3, elks='tab', wait_futures=second_futures+futures)

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



if __name__ == '__main__':

    res = main()
    print(res)

