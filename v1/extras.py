
import random, asyncio, os

import concurrent.futures


async def async_sleep_tick(i, *a, **kw):
    m = (i % 10) * .2 + random.random()
    d = 1 + m
    v = kw.get('text', 'async_sleep_tick')
    print(f"{'pid':<6}", f"{'#':<3}", f"{'delay':<7}", 'label')

    while 1:
        n = round(m,4)
        print(f"{os.getpid():<6}", f"{i:<3}", f"{n:<7,} ", v)
        await sleep_loop(d)


async def sleep_loop(timeout):
    await asyncio.sleep(timeout)


def wait_futures(futures):
    concurrent.futures.wait(futures)
    for future in concurrent.futures.as_completed(futures):
        # url = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print(f'{future} generated an exception: %s' % (exc))
        else:
            print(data)

    return futures
