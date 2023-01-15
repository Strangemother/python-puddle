# Python Puddles

> `Puddles` provdes a range of tools to simplify the execution and management of multiprocessing Pools and Processes.


To get started install:

    pip install puddles

Job done. All dependencies are built-ins.

## Example

+ Run a async and non-async
+ with args, and kwargs
+ and iterable unpacks:

```py
import puddles
from puddles import raw, extras


def sync_sleep(index=-1, **other):
    print('sync_sleep', 'index:', index, 'options:', other)
    time.sleep(extras.variate(3, .5))
    return index


async def async_sleep(index=-1, **other):
    print('async_sleep', 'index:', index, 'options:', other)
    await asyncio.sleep(extras.variate(3, .5))
    return index


def generate_function_pack(func):
    items = (
                # # Function
                func,
                # # Function and args
                (func, (2,)),
                # # function, args, kwargs
                (func, (3,), { 'roo': 'berry'}),
                # # A 'unit' of all func, args, kwargs
                raw.unit(func, 4, foo='bar'),
                # # many units ...
                raw.count(2, func, "5/6", elk='Ricky'),
        )
    return items

# For fun, generate the same function signatures for sync and async
items = generate_function_pack(async_sleep)
items += generate_function_pack(sync_sleep)

len(items) == 10

# Run them all...
result = puddles.run(items)
print(result)
# (4, -1, 4, '5/6', 2, 3, '5/6', -1, 2, '5/6', '5/6', 3)
```

And you're good to go. As all `items` standard Futures, all builtins and functionality should work as expected.


## Getting Started

There is no setup process. Under-the-hood `puddles` uses the `concurrent.futures` multiprocessing library.

To run a function on another process use `puddles.run(func, *a, **kw)`

```py
import puddles

def process_func():
    print('Process execution')
    puddles.extras.sync_sleep(3) # not async.
    return 'egg'

results = puddles.run(process_func)
# ('egg',)
```

`puddles` runs async functions automatically `puddles.run(async_func(*a, **kw))`:

```py
import puddles

async def async_process_func(timeout=3):
    print('Async Process execution')
    await puddles.extras.async_sleep(timeout) # is async.
    return timeout

results = puddles.run(async_process_func)
# (3, )
```

To run many functions, provide a `tuple` of callables. Both async and none-async will run:

```py
import puddles

functions = (
        process_func,   # from the above example
        async_process_func, # also from above.
    )

results = puddles.run(functions)
# ('egg', 3, )
```


## Args and Kwargs

Provide arguments to the immediate executor:

```py
import puddles

async def process_func(timeout=2):
    print('Process execution timeout:', timeout)
    await puddles.extras.async_sleep(timeout)
    return timeout

puddles.run(process_func, 3)
# (3,)
```

For multiple functions, provide a tuple of tuples:

```py
import puddles

async def process_func(timeout=3):
    print('Process execution timeout:', timeout)
    await puddles.extras.async_sleep(timeout)
    return timeout

sigs = (
    (process_func, ),
    (process_func, (2,)),
    (process_func, (), {'timeout': 1})
)

puddles.run(sigs)
# (1,2,3)
```


## Stacking `run()` and Non-Blocking Starts

We can bypass _waiting_ until the futures are complete, by providing `wait_futures=False` to the `run` method.

The futures return immediately - Therefore we can quickly submit more tasks:

```py
import puddles

async def process_func(timeout=2):
    print('Process execution timeout:', timeout)
    await puddles.extras.async_sleep(timeout)
    return timeout

futures = puddles.run(process_func, 3, wait_futures=False)
## non-blocking - return a <future> immediately
results = puddles.run(process_func, timeout=3, wait_futures=futures)
## ... block 3 seconds ...
# (3, 3)
```

### Waiting with `wait_futures(futures:iterable)`


There is no limit to the count of `run()` calls. Additionally the `extras.wait_futures` method provides a convenient wait handler:


```py
import puddles
from puddles import extras

async def process_func(timeout=2):
    print('Process execution timeout:', timeout)
    await puddles.extras.async_sleep(timeout)
    return timeout

futures =  puddles.run(extras.async_sleep, 3, wait_futures=False)
futures += puddles.run(extras.sync_sleep, 5, wait_futures=False)
futures += puddles.run(extras.async_sleep, 2, wait_futures=False)

others = puddles.run(process_func, 4, wait_futures=False)
## non-blocking - return a <future> immediately

results = puddles.run(process_func, timeout=3, wait_futures=futures+others)
futures, data = extras.wait_futures(results)
# ... block and wait ...
````


## Running `unit(func, *a, **kw)` callers

To clean up the setup of callable functions, the `puddle.unit()` function bundles
all the arguments into a single ready-to-go callable, it can replace a tuple within
the runnables:

```py
import puddle, extras


async def func(index=-1, **other):
    """Function ran on the new CPU Process.
    """
    print('func', 'index:', index, 'options:', other)
    return index


items = (
        # # function, args, kwargs
        (func, (3,), { 'roo': 'berry'}),
        # # A 'unit' of all func, args, kwargs
        puddle.unit(func, 4, foo='bar'),
        puddle.unit(func, 4, foo='bar'),
        puddle.unit(func, 4, foo='bar'),
)

puddle.run(items)
# (3, 4, 4, 4, "5/6", "5/6")
```

## Many units with `count(i, func, *a, **kw)`

Rather than run many `unit()` items, we can replace then with a single `count()`
of many items. They can be stacked:

```py
import puddle, extras


async def func(index=-1, **other):
    """Function ran on the new CPU Process.
    """
    print('process_function', 'index:', index, 'options:', other)
    return index

def other_func(index=909):
    """Function ran on the new CPU Process.
    """
    print('other_func')
    return index


items = (
        puddle.unit(func, 1, foo='bar'),
        # 5 units ...
        puddle.count(5, func, 2, elk='Ricky'),
        # another 3
        puddle.count(4, other_func),
)

puddle.run(items)
# (1, 2, 2, 2 ,2, 909, 2, 909, 909, 909)
```

Any threadsafe arguments are compatible, and the entry function e.g. `other_func` may be `async` or not-async.

Futhermore, this works with all other setup methods:

```py
import puddle


def generate_function_pack(func):
    """Generate a list of example runnables for the run().
    """
    items = (
            # proc.extras.async_sleep_tick(2),
            # # Function
            func,
            # # Function and args
            (func, (2,)),
            # # function, args, kwargs
            (func, (3,), { 'roo': 'berry'}),
            # # A 'unit' of all func, args, kwargs
            raw.unit(func, 4, foo='bar'),
            # # many units ...
            raw.count(2, func, "5/6", elk='Ricky'),
    )
    return items


items = generate_function_pack(sync_sleep)
puddle.run(items)
```

# Process Head

Puddle applies a "head" for the execution of each new process. The head accepts all the arguments given to the new process and is designed offset the hard-parts of running a function. This includes detecting async routines and special parameters.

The package silently applies a caller function `puddles.raw.primary_head_main(func, *a, **kw)` of which runs a new `puddles.head.ProcessHead` to run your code.

Functionally this is synonymous to:

```py
import puddles

# run 10 items but open 5 cpu processes,
# forcing 2 tasks per thread
packs = (
        func,
        puddles.count(9, func),
    )

puddles.raw.submit(
    items=packs,

    ## No count opens n=len(packs)
    ## less than {n} will execute {count} until a thread death,
    ## spawning a new task until exausted.
    count=5,
    # don't run the given func, rather assign it to an
    # 'accepting' func to offload execution.
    head_caller=puddles.head.primary_head_main,
)
```


## `ProcessHead` Class

The ProcessHead or generally a _head class_ is the unit owning the execution of the function within the new process. It maintains a range of functions to leverage the given function, and any wrappers for special arguments and close the function.

    __main__ -> puddle.run(callable) -> new process -> ProcessHead -> [callable]
                                                    -> ProcessHead -> [callable]
                                                    ...
                                     -> new process -> ProcessHead -> [callable]
                                    ...


By default a `puddles.head.InfoHead` (or child) will run the code. This is generated through the `head_caller`. The class instance runs within the new process.

A new `head_class` can be supplied to alter the default. Note we can provide a string here or a class


```py
import puddles

def func(*a, **kw):
    print('proc func', a, kw)


packs = (
        func,
        puddles.count(12, func),
    )


class CustomHead(puddles.head.InfoHead):

    def setup(self):
        """A hook for process starts"""
        print('New Process', self.kwargs)


puddles.raw.submit(
    items=packs,

    ## No count opens n=len(packs)
    ## less than {n} will execute {count} until a thread death,
    ## spawning a new task until exausted.
    count=5,

    # don't run the given func, rather assign it to an
    # 'accepting' func to offload execution.
    head_class=CustomHead,
)
```
