import asyncio
from pydoc import locate as pydoc_locate

locate = pydoc_locate


class Shadow(object):
    _shadow_default_compiler = 'shadow_dict_compiled'
    _shadow_current_compiler = _shadow_default_compiler
    _shadow_keystack = None

    def __init__(self, *a, _shadow_keystack=None, _shadow_current_compiler=None, **kw):
        self._shadow_pre_args = a
        self._shadow_pre_kwargs = kw
        self._shadow_keystack = _shadow_keystack or ()
        self._shadow_current_compiler = _shadow_current_compiler or self._shadow_current_compiler

    def __getattr__(self, k):
        return self.__class__(
            *self._shadow_pre_args,
            _shadow_keystack=self._shadow_keystack + (k,),
            _shadow_current_compiler=self._shadow_current_compiler,
            **self._shadow_pre_kwargs,
        )

    def __call__(self, *a, **kw):
        return self.shadow_call_compiled(a, kw)

    def shadow_set_compiler(self, v):
        if v is None:
            v = self._shadow_default_compiler
        self._shadow_current_compiler = v

    def shadow_call_compiled(self, a, kw):
        current = self._shadow_current_compiler
        if callable(current):
            func = current
            return func(self, *a, **kw)

        return getattr(self, current)(a, kw)
        # return self.dict_compiled(a, kw)

    def shadow_path_compiled(self, a=None, kw=None):
        return self.shadow_get_dotstring()

    def shadow_execute_compiled(self, a, kw):
        return self.shadow_discover_callable()(*a, **kw)
        # return self.dict_compiled(a, kw)

    def shadow_discover_callable(self):
        return pydoc_locate(self.shadow_get_dotstring())

    def shadow_str_compiled(self, a, kw):
        a_str = ', '.join(map(lambda x: x.__repr__(), a))
        kv = ""
        for x, y in kw.items():
            kv += f', {x}={y}'
        return f"{self.shadow_get_dotstring()}({a_str}{kv})"

    def shadow_dict_compiled(self, a, kw):
        return dict(
            path=self.shadow_get_dotstring(),
            args=a,
            kwargs=kw,
            pre_args=self._shadow_pre_args,
            pre_kwargs=self._shadow_pre_kwargs,
        )

    def shadow_get_dotstring(self, *a, **kw):
        return '.'.join(self._shadow_keystack)

    def __str__(self):
        s = self.shadow_get_dotstring()
        return s

    def __repr__(self):
        c = self.__class__.__name__
        s = self.shadow_get_dotstring()
        return f'<{c} "{s}">'

