
from run import Shadow

a = (1, True, 'tup',)
kw = dict(elk=1, boof=2)
s = Shadow(*a, **kw)

baz = s.foo.bar.baz

assert baz.shadow_get_dotstring() == 'foo.bar.baz'
assert baz._shadow_pre_kwargs == kw
assert baz._shadow_pre_args == a

baz.shadow_set_compiler('shadow_str_compiled')
vv = baz(1,1, 'apples', globals, foo=2, elk=True)
expected = "foo.bar.baz(1, 1, 'apples', <built-in function globals>, foo=2, elk=True)"

assert vv == expected

baz.shadow_set_compiler(None)
expected = {
    'path': 'foo.bar.baz',
    'args': (1, 1, 'apples', globals),
    'kwargs': {'foo': 2, 'elk': True},
    'pre_args':(1, True, 'tup'),
    'pre_kwargs': {'elk': 1, 'boof': 2}
    }
vv = baz(1,1, 'apples', globals, foo=2, elk=True)
assert vv == expected


ret_math = s.foo.bar.ret_math
ret_math.shadow_set_compiler('shadow_execute_compiled')

assert ret_math(1,1) == 2
assert ret_math(10,2, op='sub') == 8

def merge_func(shadow, *args, **kwargs):
    func = shadow.shadow_discover_callable()
    a = shadow._shadow_pre_args + args
    kw = shadow._shadow_pre_kwargs.copy()
    kw.update(kwargs)
    return func(*a, **kw)

s.shadow_set_compiler(merge_func)
baz = s.foo.bar.baz

vv = baz(sum, elk=False, other='yes')
expected = (
    (1, True, 'tup', sum),
    {'elk': False, 'boof': 2, 'other': 'yes'}
)
assert vv == expected
