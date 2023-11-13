
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
        await async_sleep(d)

from time import sleep as time_sleep


def sync_sleep(timeout):
    time_sleep(timeout)
    return timeout


async def async_sleep(timeout):
    await asyncio.sleep(timeout)


def wait_futures(futures):
    print(f'extras.wait_futures for {len(futures)} items')
    res = soft_wait_futures(futures)
    print('extras.wait finished waiting. Result count:', len(res))
    return res


def full_wait_futures(futures):
    concurrent.futures.wait(futures)
    return soft_wait_futures(futures)


def soft_wait_futures(futures):
    res = ()
    print(f'soft_wait {len(futures)} futures...')
    for future in concurrent.futures.as_completed(futures):
        # url = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print('\ngenerated an exception: %s' % (exc))
        else:
            print('Item Complete:', future.index)
            print('Storing', data)
            res += (data,)
    print('Returning results, len', len(res))
    return futures, res


def wait_futures_more(futures):
    print(f'wait_futures for {len(futures)} items')
    concurrent.futures.wait(futures)
    cindex = 0

    res = {'fails': (), 'complete': (), 'count': len(futures)}

    for future in concurrent.futures.as_completed(futures):
        # url = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print('\ngenerated an exception: %s' % (exc))
            res['fails'] += ((cindex, future,),)
        else:
            # print(data)
            res['complete'] += ((cindex, future, data,),)
            cindex += 1
    res['size'] = cindex

    return res


def clean_futures(futures):

    cindex = 0

    res = {'fails': (), 'complete': (), 'count': len(futures)}

    for future in concurrent.futures.as_completed(futures):
        # url = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print('\ngenerated an exception: %s' % (exc))
            res['fails'] += ((cindex, exc,),)
        else:
            res['complete'] += ((cindex, data,),)
            cindex += 1
    res['size'] = cindex
    return res



import time

def variate(i, v=.2):
    return (i % 10) * v + random.random()


def sleep_tick(i, *a, **kw):
    m = variate(i)
    d = 1 + m
    v = kw.get('text', 'sleep_tick')
    print(f"{'pid':<6}", f"{'#':<3}", f"{'delay':<7}", 'label')

    while 1:
        n = round(m,4)
        print(f"{os.getpid():<6}", f"{i:<3}", f"{n:<7,} ", v)
        time.sleep(d)

