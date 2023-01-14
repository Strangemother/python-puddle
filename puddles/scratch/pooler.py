import sys, os
import asyncio, time
import concurrent.futures

import multiprocessing
import extras, generic



def submit(*packs, count=-1):
    futures = None
    try:
        futures = run_all(*packs, count=count)
        print('Futures', futures)
        futures = extras.wait_futures(futures)
    except KeyboardInterrupt:
        print('KB Kill top level')
    return futures


class Async(object):
    count = 1
    offset = 0
    flat = False
    headless = False

    def __init__(self, func, *args, count=-1, offset=0):
        self.func = func
        self.args = tuple(args)
        self.offset = 0
        self.count = self.count if count == -1 else count

    def __iter__(self):
        for i in range(self.offset, self.count+self.offset):
            yield self.pool_pack(i)

    def promise_set(self):
        return (self.func, self.args, )

    def pool_pack(self, i):
        ps = self.promise_set()
        func, (*aa,) = ps
        aa = tuple(aa)
        if self.headless is False:
            func = generic.async_head
            aa = ps

        if self.flat:
            return (func,) + self.prepare_pool_pack_args(aa, i)
        return func, self.prepare_pool_pack_args(aa, i)

    def prepare_pool_pack_args(self, aa, i):
        return aa

    def __len__(self):
        return self.count


class Sync(Async):
    flat = True
    headless = True

    # def prepare_pool_pack_args(self, aa, i):
    #     return aa + (i+self.offset, )


from inspect import iscoroutinefunction as is_async

def run_all(*method_packs, count=-1):

    tasks = ()
    for pack in method_packs:
        if hasattr(pack, '__iter__'):
            # Unpack iterables such as the Count and lists
            for promise_set in pack:
                tasks += (promise_set,)
            continue

        if callable(pack):
            # Is a func run_all(func_a, func_b, ...
            # # Apply as a list of one item, the callable with no args.
            tasks += ( (pack,),)
            continue


    l = len(tasks)
    t = l if count < 0 else count
    print(f'Built {l} tasks, running {t} live processes')

    futures = ()
    # read_pipe, write_pipe = os.pipe()
    read_pipe, write_pipe = multiprocessing.Pipe()

    with concurrent.futures.ProcessPoolExecutor(t) as pool:
        for i, pack in enumerate(tasks):
            func = pack[0]
            if is_async(func):
                # this will fail.
                print(f'An async primary function needs an executor, #{i} may fail.')
            nt = pool.submit(*pack)
            futures += (nt, )
        # for i in range(0, count-1):
        #     nt = pool.submit(primary_proc_main, i, read_pipe)
            # futures += (nt, )
    return futures

