import asyncio
import concurrent.futures

import extras
import pooler


HOST = '127.0.0.1'
DEBUG = True
PORT = 0

def name_main():

    primary = pooler.Async(proc_server, proc_socket_handler, count=1)
    secondaries = ()# pooler.Sync(primary_proc_main, count=10, offset=1)
    thirds =  pooler.Async(a_primary_proc_main, count=10, offset=11)
    return pooler.submit(primary, secondaries, thirds, count=-1)


def inline_caller():
    """Shadow the callable with args and kwargs
    pre-args call to the internal properities of the _Head_

    """
    # await proc_server(i, pipes, count=-1)
    caller(proc_server, props.index, pipes=props.pipes, count=props.count, )


def primary_proc_main(*a, **kw):
    print('primary_proc_main', a, kw)
    try:
        asyncio.run(extras.async_sleep_tick(*a, **kw))
    except KeyboardInterrupt:
        print('KB Kill',a)


async def a_primary_proc_main(*a, **kw):
    # if len(a[0]) == 0: a = (1,)
    print('a_primary_proc_main', a, kw)
    try:
        await extras.async_sleep_tick(*a, text='a_primary_proc_main tick')
    except KeyboardInterrupt:
        print('KB Kill',a)


async def proc_server(socket_handler):
    # proc_socket_handler
    server = await asyncio.start_server(socket_handler, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)

    # https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.Server.serve_forever
    async with server:
        print(f'Serving on {addrs}')
        await server.serve_forever()


async def proc_socket_handler(reader, writer):
    """Given to the proc_server function for the socket handler.
    """
    addr = writer.get_extra_info('peername')
    connected = 1
    parts = ()
    while connected:
        data = await reader.read(100)
        parts += (data.decode(),)

    print(f"-- Received {parts!r} from {addr!r}")

    print(f"-- Send: {milk!r}")
    writer.write('milk')
    await writer.drain()


if __name__ == "__main__":
    name_main()

