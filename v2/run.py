from inspect import iscoroutinefunction as is_async, iscoroutine as is_co

import raw, asyncio, extras
import shadow
import time

proc = shadow.Shadow()

import metakey

def main():
    meta = metakey.meta

    packs = (
        ## Run a method with meta arguments for the target func.
        ### Any additionl args here appear within the head_accept func.
        raw.unit(head_accept, meta.head, pids=meta.pids, index=meta.index),
        ## Multiply this job by {n}
        raw.count(10, head_accept, meta.head, index=meta.index),
    )

    # These options appear within the primary head_caller function
    return raw.run(packs, head_class='head.InfoHead')


def other_main():
    sleep_packs = (

        ## Run a _standard_ method with args, [kwargs]
        (extras.sleep_tick, (2,) ),

        ## Call a non-async func using a lazy shadow string
        proc.extras.sleep_tick(1),

        ## Run an async method
        proc.extras.async_sleep_tick(2),

        # raw.count(...) of 1
        raw.unit(extras.sleep_tick, 1),

        ## Call a function with the Options convenience
        raw.count(1, extras.sleep_tick, 1),
        raw.count(1, extras.sleep_tick, i=1),

        ## execute a tuple pack of func, args, kwargs
        raw.count(1, (extras.sleep_tick, (1,), ) ),
        raw.count(1, (extras.sleep_tick, (), {'i': 2} ) ),

        ## Run a loaded shadow
        raw.count(1, proc.extras.sleep_tick(1)),

        ## Run an async metho
        raw.count(5, proc.extras.async_sleep_tick(2) ),
    )

    return raw.run(sleep_packs)

    # return raw.submit(
    #         items=packs,
    #         ## No count opens n=len(packs)
    #         ## less than {n} will execute {count} until a thread death,
    #         ## spawning a new task until exausted.
    #         # count=2,

    #         # don't run the given func, rather assign it to an
    #         # 'accepting' func to offload execution.
    #         head_caller=primary_head_main,
    #         )


def head_accept(head, index=-1, **other):
    """Run a method as a raw unit with meta arguments:

        >>> raw.unit(head_accept, meta.head, index=meta.index),
        head_accept <__mp_main__.ProcessHead object> index 0

    In this example we return the call index of the thread.
    """
    print('head_accept', head, 'index:', index, 'other options:', other)
    time.sleep(extras.variate(3))
    return index

if __name__ == '__main__':
    res = main()
    print(res)
    # other_main()
