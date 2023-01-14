import time

from puddles import raw, extras

def main():
    """Run a single function with args and kwargs"""
    return raw.run(sync_sleep, 1, foo='bar')


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

