import concurrent.futures
import extras

def submit(items, count=-1):
    futures = None
    try:
        futures = run_all(*items, count=count)
        print('Futures', futures)
        futures = extras.wait_futures(futures)
    except KeyboardInterrupt:
        print('KB Kill top level')
    return futures


# from inspect import iscoroutinefunction as is_async


def run_all(*tasks, count=-1):
    futures = ()
    t = len(tasks) if count < 0 else count
    with concurrent.futures.ProcessPoolExecutor(t) as pool:
        for i, pack in enumerate(tasks):
            nt = pool.submit(pack)
            futures += (nt, )
        # for i in range(0, count-1):
        #     nt = pool.submit(primary_proc_main, i, read_pipe)
            # futures += (nt, )
    return futures

