# Notes

The first version works very well and shows the async pool is quick to deploy.
The second version proves it's better to wrap the start process of every process with a 'head', allowing the integration of key annotations when executing the process.

+ Index
+ Pipes
+ args ...

The user may choose to leverage the head, or it's implemented silently. Additionally we can program the head to run the given function reglardless of its coroutine processing.

```PY
# builds a prep.
pool.submit(async_function, *args, **kwargs)
pool.submit(sync_function, *args, **kwargs)
# or of both
pool.submit(prep_instance)
```

A prep reprents the start tool for a process:

```py
class Prep:

    init(func, args, kwargs):
        ...
```

Each process has a _Head_ to execute the proc data.

```py
def process_main(index, pipes, func, *a,**kw):
    head = Head(*a, **kw)
    asyncio.run(head.executor())
```

The head maintains all the important elements of the new process and can execute the user defined process within the async process. The function may be non-async.

A head has a book of methods to facilitate communication to the parent. This can be ignored for silent execution.


## actions

The head may receive special messages - such as an executable to run. This is done through dotted notation strings, gathered and executed using good old fashion pylocate.

The head recieves a pipe message `foo.download_iso`, with args `linux_123`, to run in the prepared function. The result is stored and the answer is piped.

Deeper integration can be yaml based loadouts in a shared db.

## pipes

The async pipes are applied to the head through the executor startup, They pipe bound messages to the primary for a central hub.

In personal additions the head will load messages as piped tasks, returning the result back the primary for processing.

pop piping should allow processes to communicate other processes, without the primary as a middleman. This task should build a pair of pipes in the requesting process and push the receiver to the secondary.

## messages

The primary thread should maintain a message route for all processes. Utilising the shared manager header builtin, a localhost connection may bridge messages across primaries.


## Writes

For larger datasets and information not threadsafe, a storage method may be applied such as shared memory or file puts.

These may be given to the head as _write locations_. The input and output of the function may present information to write, handled by the head

+ pipes: the primary message header
+ Shared-memory, secondary-pipes
+ db, files


## Pop threads

Processes and threads ran by a coroutine; should as a spawn. Some limitation apply for real forkinh - but it's functional.

Secondly the head may request to push a task into the primary. Another future could be created, or if a _waiting action head_ exists, the primary could deploy a new task.

Pop threads should be available as any one of:

+ A standard async task
+ general coroutine/multiprocess calls
+ A head-> pipe message to the primary;
    + creating a new concurrent future
    + or pushing to an action client.


## Exception handling

The head handler should be able to handle exceptions of any type - build by the dev. In its route this is exposable through the given head calling function, failing this a range of builtins help with housecleaning.

One includes the keyinterrupt.

---

Additional message handling leverages internal and runtime errors. The primary may pass poison pill messages or other _commands_. Generic exceptions on the executor can bubble errors and gracefully shut-down a thread.



---

# Magic

The yielding caller is a string bound to arguments, called by a head when received through the pipe.

```py
m = magic()
func = foo.bar.baz(1,2 pop=True, ape='Teso')
# <Magic Yield>
```

Secretly a string pointing to a waiting function.

    {
        func: 'foo.bar.baz'
        args: (1,2)
        kwargs: {
            ape: "Teso"
        }
    }


The head reads this for running and yields the result. Futhermore this can be executed immediately. With a directive for functional placement:


```py
# in foo/bar.py
async def baz(*a, pop=False,ape=None):
    return sum(a)


m = magic()
func = foo.bar.baz(1,2 pop=True, ape='Teso', where='new_process')
# <Magic Yield>

val = func() # => runs in proc loop.
3
```
Therefore the magic function can call upon the function in another process without failing due to another thread.
