import time

from puddles import raw, extras, count, run, unit

def main():
    sleeps = count(2, process_func, 2)
    sleeps.add_done_callback(sleeps_done)
    sleeps2 = count(4, process_func, timeout=1.4)
    sleeps2.add_done_callback(sleeps_done)
    sigs = (sleeps, sleeps2)

    return run(sigs)
    # (1, 2, 3)

def sleeps_done(future):
    print(f'sleeps_done #{future.index}', future.result())
    ## dont run from within a future callback.
    ## this will lead to a runtime-error after 6x recurse.
    # raw.run(process_func, 2)

async def process_func(timeout=3):
    print('process_func sleep:', timeout)
    await extras.async_sleep(timeout)
    return timeout


if __name__ == '__main__':
    res = main()
    print(res)

