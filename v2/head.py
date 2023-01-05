import os
import metakey
import shadow
from inspect import iscoroutinefunction as is_async, iscoroutine as is_co
import asyncio
from functools import cached_property


class ProcessHead(object):
    """The ProcessHead acts as the primary for a new process, called upon
    by the "head_caller" through the pool.submit.

    The head should prepare an instance of this class and run .live()

        head = ProcessHead(func, *a, **kw)
        return head.live()

    Header args and kwargs assist with the preloading of the function,
    additional args are already applied within the func caller (async,)
    or assigned the the loadout of the func, such as a dict or tuple.

    """
    def __init__(self, func, *a, **kw):
        self.func = func
        self.args = a
        self.kwargs = kw
        self._livemap = {}

    def setup(self):
        ...

    def add_map(self, k, v):
        skey = metakey.skey
        self._livemap[skey(k)] = v

    def live(self, *a, **kw):
        """The first live head"""
        return self.run_func(*a, **kw)

    # @cached_property
    @property
    def key_map(self):
        skey = metakey.skey
        return {
            skey('index'): self.kwargs['index'],
            skey('head'): self,
            **self.livemap()
        }

    def livemap(self):
        return self._livemap

    def get_callable(self, *a, **kw):
        func = self.func
        if isinstance(self.func, dict):
            # unpack
            func = shadow.locate(self.func['path'])(*self.func['args'])

        if isinstance(self.func, (tuple, list)):
            func = self.func[0]
            a  = self.func[1] if len(self.func) > 1 else a
            kw  = self.func[2] if len(self.func) > 2 else kw

        return func, a, kw

    def run_func(self, *a, **kw):
        func, fargs, fkwargs = self.get_callable(*a, **kw)
        pa, pkw = metakey.proc_process_meta(self, fargs, fkwargs)
        if is_async(func) or is_co(func):
            return self.run_func_in_aync(func, *pa, **pkw)
        return func(*pa, **pkw)

    def run_func_in_aync(self, func, *a, **kw):
        try:
            return asyncio.run(func)
        except KeyboardInterrupt:
            print('Head Kill', a, kw)


class InfoHead(ProcessHead):

    def setup(self):
        super().setup()
        self.add_map('pids', self.pids)

    def pids(self):
        print('pids called')
        return (os.getppid(), os.getpid())
