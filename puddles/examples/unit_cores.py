import time
from puddles import raw, extras
import asyncio

def main():
    """In this example we run 5*2 functions. 5 async, and 5 sync sleep functions.
    Each set presents a method to integrate a function call from a list.

    We submit all 10 prepared functions to run(). It will wait for the results.

        (4, -1, 4, '5/6', 2, 3, '5/6', -1, 2, '5/6', '5/6', 3)
    """
    items = generate_function_pack(sync_sleep)
    return raw.run(items)


def generate_function_pack(func):
    items = (
            # raw.unit(func, 4, foo='bar'),
            # # many units ...
            raw.count(2, func, "5/6", elk='Ricky').cores(3,4),
    )
    return items


def sync_sleep(index=-1, **other):
    """Run a method as a raw unit with meta arguments:

        >>> raw.unit(sync_sleep, meta.head, index=meta.index),
        sync_sleep <__mp_main__.ProcessHead object> index 0

    In this example we return the call index of the thread.
    """
    print('sync_sleep', 'index:', index, 'options:', other)
    time.sleep(extras.variate(3, .5))
    return index


async def async_sleep(index=-1, **other):
    print('async_sleep', 'index:', index, 'options:', other)
    await asyncio.sleep(extras.variate(3, .5))
    return index


if __name__ == '__main__':
     res = main()
     print(res)

