
from functools import partial
from inspect import iscoroutinefunction as is_async, iscoroutine as is_co
import shadow

import concurrent.futures
import extras

def run(items, **kw):
    """Synonymous to:

        return raw.submit(
            items=packs,
            ## No count opens n=len(packs)
            ## less than {n} will execute {count} until a thread death,
            ## spawning a new task until exausted.
            # count=2,

            # don't run the given func, rather assign it to an
            # 'accepting' func to offload execution.
            head_caller=primary_head_main,
        )
    """
    kw.setdefault('head_caller', primary_head_main)
    futures, res = submit(items, **kw)
    return res
    # return clean_waits(futures)

def clean_waits(res):
    clean = extras.clean_futures(res)
    if len(clean['fails']) > 0:
        print('Some errors occured during processing')
    return extras.clean_futures(res)['complete']

from head import ProcessHead


def primary_head_main(*a, **kw):
    """
    the arguments are a list of args and kwargs expected for the header caller (a)
    The header caller may be the head_caller from a submit, or plainly the user function

    Any arguments given to the run() method appear here.

        raw.run(packs, head_class='head.InfoHead')
        # primary_head_main(head_class='head.InfoHead')
    """
    # print('primary_head_main', a, kw)
    Head = kw.get('head_class', None) or ProcessHead
    # print('primary_head_main', kw)
    if isinstance(Head, str):
        Head = shadow.locate(Head)

    _head = Head(*a, **kw)
    _head.setup()
    return _head.live()


def submit(items, count=-1, **kw):
    futures = None
    try:
        futures = run_all(*items, count=count, **kw)
        print(f'raw.submit submitted: {len(futures)} futures')
        futures = extras.wait_futures(futures)
    except KeyboardInterrupt:
        print('KB Kill top level')
    return futures


class Options(object):

    def __init__(self, func, **kw):
        self.offset = 0
        self.unpackable = True
        self.__dict__.update(kw)
        self.func = func

    def __iter__(self):
        for i in range(self.offset, self.count+self.offset):
            yield self.pool_func(i)

    def pool_func(self, i):
        # a = self.args
        # kw = self.kw
        func = self.func
        if isinstance(func, (list, tuple, dict)):
            return func
        return func, self.pre_process_args(self.args), self.pre_process_kw(self.kw)

    def pre_process_args(self, a):
        r = ()
        for v in a:
            if isinstance(v, shadow.Shadow):
                r += (v.shadow_path_compiled(),)
                continue
            r+=(v,)
        return r

    def pre_process_kw(self, kw):
        r = {}
        for k,v in kw.items():
            if isinstance(v, shadow.Shadow):
                v = v.shadow_path_compiled()
            r[k]=v
        return r

    def get_func(self):
        a = func['args']
        kw = func['kwargs']

        if isinstance(func, dict):
            # unpack
            func = shadow.locate(func['path'])
            print('async func', func)

        if is_async(func) or is_co(func):
            print('return async', func, a, kw)
            return func(*a, **kw)

        return partial(func, *a, **kw)


def unit(func, *a, **kw):
    return count(1, func, *a, **kw)


def count(count, func, /, *a, **kw):
    return Options(func, count=count, args=a, kw=kw)


def unpack_tasks(tasks):
    funcs = ()
    for i, pack in enumerate(tasks):
        if hasattr(pack, 'unpackable') is False:
            pack = (pack,)

        for func in pack:
            funcs += (func, )
    return funcs


def early_mentions(funcs, count):
    l = len(funcs)

    if l < count:
        print(f'\n  Warning: Counts ({count}) greater than tasks ({l})'
                ' will lead to empty processes.\n')
    if l > count:
        print(f'\n  Notice: A pool count ({count}) less than '
            f'the task count ({l}) will run a reduce-stack.\n')


def run_all(*tasks, count=-1, head_caller=None, concurrency_class=None, **shared_options):
    funcs = unpack_tasks(tasks)

    t = len(funcs) if count < 0 else count
    early_mentions(funcs, t)

    return futures_pool(funcs, count=count,
                        func=head_caller,
                        concurrency_class=concurrency_class,
                        shared_options=shared_options)


def futures_pool(items, count=-1,
                 func=None,
                 shared_options=None,
                 concurrency_class=None,
                 ):
    t = len(items) if count < 0 else count

    Executor = concurrency_class or concurrent.futures.ProcessPoolExecutor
    if isinstance(Executor, str):
        Executor = shadow.locate(Executor)

    pool = Executor(t)

    futures = ()
    for i, pack in enumerate(items):
        a = (pack, )
        kw = (shared_options or {}).copy()
        if func is not None:
            # The head accepts initial args to extend the basic loop.
            # A head accepting all args, and rebinds in the process
            # to populate a processhead
            a = (func,) + a
            kw.update({'index': i})
        nt = pool.submit(*a, **kw)
        nt.index = i
        futures += (nt, )

    return futures

