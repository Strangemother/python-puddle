
from functools import partial
from inspect import iscoroutinefunction as is_async, iscoroutine as is_co
import concurrent.futures

from .head import ProcessHead

from . import shadow
from . import extras

def run(items, *run_args, **kw):
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
    pop_default(kw, 'head_caller', primary_head_main)
    pop_default(kw, 'args', run_args)
    wait = pop_default(kw, 'wait_futures', True) is not False
    print('Wait', wait)
    print(kw)
    futures_set = submit(items, **kw)
    if wait is not False:
        futures, res = futures_set
        return res
    return futures_set
    # return clean_waits(futures)


def pop_default(kw, k, v):
    kw.setdefault(k, kw.pop(k, v))
    return kw[k]


def clean_waits(res):
    clean = extras.clean_futures(res)
    if len(clean['fails']) > 0:
        print('Some errors occured during processing')
    return extras.clean_futures(res)['complete']


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
    """Run many _items_ being functions or unapckable iterables,
    returning a list of waited futures.
    """
    futures = None


    run_args = kw.pop('args', ())
    run_kwargs = kw.pop('kwargs', kw)
    head_caller = kw.pop('head_caller', None)
    # wait_futures = kw.pop('wait_futures', None)

    given_futures = kw.pop('wait_futures', None)
    print(items)
    if hasattr(items, 'unpackable') is True:
        print('is unpackable')
        items.run_kwargs = run_kwargs
        items.run_args = run_args
        items = (items,)

    elif callable(items):
        items = (
            (items, run_args, run_kwargs,),
        )
    else:
        # Reapply to the dict, pushed into the _shared_options_ appearing
        # in the Head.kwargs['run_kwargs'], used by Head.get_callable
        # during instansiation
        #
        # Note, this must be applied to the core dict as
        # nested dicts are unhashable.
        kw.update(run_kwargs)
        kw['run_args'] = run_args

    futures = unpack_to_futures(*items, count=count, head_caller=head_caller, **kw)
    print(f'raw.submit submitted: {len(futures)} futures')

    extra_futures = ()
    if isinstance(given_futures, bool) is False:
        extra_futures = given_futures
    futures += extra_futures

    wait_futures = given_futures not in (False, None,)
    print('wait futures', wait_futures)
    if wait_futures:
        try:
            return extras.wait_futures(futures)
        except KeyboardInterrupt:
            print('KB Kill top level.')

    return futures


class Options(object):

    def __init__(self, func, **kw):
        self.offset = 0
        self.unpackable = True
        self.__dict__.update(kw)
        self.func = func

    def __iter__(self):
        for i in range(self.offset, self.count+self.offset):
            yield self.get_yield_result(i)

    def get_yield_result(self, i):
        return self.pool_func(i)

    def pool_func(self, i):
        """Return the function of index for the pool. This is given to the submit
        function.
        """
        # a = self.args
        # kw = self.kw
        func = self.get_future_func()
        if isinstance(func, (list, tuple, dict)):
            """Return the prepared function"""
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

    def get_future_func(self):
        return self.func

    def get_func(self):
        a = self.func['args']
        kw = self.func['kwargs']

        if isinstance(func, dict):
            # unpack
            func = shadow.locate(func['path'])
            print('async func', func)

        if is_async(func) or is_co(func):
            print('return async', func, a, kw)
            return func(*a, **kw)

        return partial(func, *a, **kw)


class Extendables(Options):
    """Provide additional functions to the unit response for callbacks
    and futures packs.
    """
    def __init__(self, func, **kw):
        self.done_callbacks = ()
        self.run_kwargs = {}
        self.run_args = ()

        super().__init__(func, **kw)

    def pre_process_args(self, a):
        a = super().pre_process_args(a)
        return a + self.run_args

    def pre_process_kw(self, kw):
        kw = super().pre_process_kw(kw)
        kw.update(self.run_kwargs)
        return kw

    def get_future_func(self):
        return self.func

    def get_yield_result(self, i):
        self._i = i
        return self

    def add_done_callback(self, callback):
        """Add a callback to the task when its created. This callback
        is given to all units extending these options.
        """
        self.done_callbacks += (callback,)

    def submit(self, pool, func, *a, **kw):
        r = (func,) + a + (self.pool_func(self._i),)
        future = pool.submit(*r, **kw)
        if len(self.done_callbacks) > 0:
            future.add_done_callback(*self.done_callbacks)
        return future


def unit(func, *a, **kw):
    return count(1, func, *a, **kw)


def count(count, func, /, *a, **kw):
    return Extendables(func, count=count, args=a, kw=kw)


def unpack_tasks(tasks):
    """Unpack a list of tasks into a tuple of individual tasks.

    Parameters
    ----------
    tasks : iterable
        An iterable of tasks, where each task may be a single callable object
          or an iterable of callable objects. If the attribute `unpackable` is
          True for a task, it will be unpacked into its individual callable
          objects.

    Returns
    -------
    tuple
        A tuple of individual tasks, in the same order as the input tasks.
    """
    funcs = ()
    for i, pack in enumerate(tasks):
        if hasattr(pack, 'unpackable') is False:
            pack = (pack,)

        for func_pack in pack:
            unpacked_test(func_pack,i)
            funcs += (func_pack, )

    return funcs


def unpacked_test(func_pack,i):
    ## An early test to ensure the arguments are applied
    # correctly:
    if not isinstance(func_pack, (tuple, list)):
        return

    if len(func_pack) <= 1:
        return

    if not hasattr(func_pack[1], '__iter__'):
        err_s = (f"Element({i}) list or tuple "
                f"second argument must be iteratable."
                f' Given: {type(func_pack[1]).__name__} "{func_pack[1]}"')
        raise Exception(err_s)


def early_mentions(funcs, count):
    l = len(funcs)

    if l < count:
        print(f'\n  Warning: Counts ({count}) greater than tasks ({l})'
                ' will lead to empty processes.\n')
    if l > count:
        print(f'\n  Notice: A pool count ({count}) less than '
            f'the task count ({l}) will run a reduce-stack.\n')


def unpack_to_futures(*tasks, count=-1, head_caller=None, concurrency_class=None, **shared_options):
    """Run a list of tasks concurrently using a specified concurrency class.

    Parameters
    ----------
    tasks : tuple
        A tuple of tasks to be run concurrently. Each task should be a callable
         object (e.g., a function).
    count : int
        The maximum number of tasks to run concurrently. If `count` is
         negative, all tasks will be run concurrently.
    head_caller : callable or str
        A callable object (e.g., a function) that is called with each task as
         its argument before the task is run. If `head_caller` is a string,
          it will be resolved within the new process and act as an
           intermediary for the new process and the given tasks.
    concurrency_class : type
        A class that is used to manage the concurrency of the tasks. The
         class should implement the `map` method, which should behave
          similarly to the built-in `map` function. If `concurrency_class`
           is not provided, the default concurrency class
            `concurrent.futures.ProcessPoolExecutor` will be used.
    **shared_options :
        Options to be shared among all tasks. These options will be passed
         as keyword arguments to each task.

    Returns
    -------
    list of futures
        A list of futures representing the results of each task, in the
         same order as the input tasks.
    """
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
    """Run a list of items concurrently using a specified concurrency class.

    Parameters
    ----------
    items : iterable
        An iterable of items to be run concurrently.
    count : int
        The maximum number of items to run concurrently. If `count` is
         negative, all items will be run concurrently.
    func : callable
        A callable object (e.g., a function) that is called with each item as
         its argument before the item is run.
    shared_options : dict
        Options to be shared among all items. These options will be passed
         as keyword arguments to each item.
    concurrency_class : type
        A class that is used to manage the concurrency of the items. The
         class should implement the `map` method, which should behave
          similarly to the built-in `map` function. If `concurrency_class`
           is not provided, a default concurrency class will be used.

    Returns
    -------
    list of futures
        A list of futures representing the results of each item, in the same order as the input items.
    """
    t = len(items) if count < 0 else count

    Executor = concurrency_class or concurrent.futures.ProcessPoolExecutor
    if isinstance(Executor, str):
        Executor = shadow.locate(Executor)

    pool = Executor(t)

    futures = ()
    for i, pack in enumerate(items):
        pack_caller = pack.get_future_func() if hasattr(pack, 'get_future_func') else pack
        a =  (pack_caller, )

        kw = (shared_options or {}).copy()
        if func is not None:
            # The head accepts initial args to extend the basic loop.
            # A head accepting all args, and rebinds in the process
            # to populate a processhead
            a = (func,) + a
            kw.update({'index': i})


        if hasattr(pack, 'submit'):
            nt = pack.submit(pool, func, **kw)
        else:
            nt = pool.submit(*a, **kw)
        nt.index = i
        nt.pool = pool
        futures += (nt, )

    return futures


