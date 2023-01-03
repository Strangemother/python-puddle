import sys, os
import asyncio, time
import concurrent.futures


HOST = '127.0.0.1'
DEBUG = True
PORT = 0

def name_main():
    try:
        futures = run_all()
        print('Futures', futures)
        wait_futures(futures)
    except KeyboardInterrupt:
        print('KB Kill')


import multiprocessing


def run_all(count=50):

    futures = ()
    # read_pipe, write_pipe = os.pipe()
    read_pipe, write_pipe = multiprocessing.Pipe()

    with concurrent.futures.ProcessPoolExecutor(count) as pool:
        nt = pool.submit(first_process, write_pipe)
        futures += (nt, )
        for i in range(0, count-1):
            nt = pool.submit(primary_proc_main, i, read_pipe)
            futures += (nt, )

    return wait_futures(futures)


def wait_futures(futures):
    concurrent.futures.wait(futures)
    for future in concurrent.futures.as_completed(futures):
        # url = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print('generated an exception: %s' % (exc))
        else:
            print(data)

    return futures


def primary_proc_main(*a, **kw):
    try:
        asyncio.run(async_primary_main(*a, **kw))
    except KeyboardInterrupt:
        print('KB Kill',a)

import random

async def async_primary_main(i, *a, **kw):
    m = (i % 10) * .2 + random.random()
    while 1:
        print('async_primary_main', os.getpid() ,   i, m)
        await sleep_loop(1 + m)


async def sleep_loop(timeout):
    await asyncio.sleep(timeout)


async def async_recv(conn):
    # Asynchronously receive data from the pipe
    while True:
        try:
            data = await asyncio.wait_for(conn.recv(), timeout=1.0)
            print(data)
        except EOFError:
            # Pipe has been closed, break out of the loop
            break


def first_process(pipe=None):
    asyncio.run(proc_server(proc_socket_handler))


async def proc_server(handler, write_pipe=None):
    server = await asyncio.start_server(handler, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    # https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.Server.serve_forever
    async with server:
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

    # print("-- Close the connection")
    #writer.close()


def slow_loop():
    while 1:
        print('slow_loop')
        time.sleep(2)


# def single_writer_pipe():
#     read, write = os.pipe()
#     writer_process = multiprocessing.Process(target=writer, args=(write,))
#     writer_process.start()
#     asyncio.get_event_loop().run_until_complete(reader(read_pipe))


async def async_pipe_reader(read_pipe):
    pipe = os.fdopen(read_pipe, mode='r')

    loop = asyncio.get_event_loop()
    stream_reader = asyncio.StreamReader()

    def protocol_factory():
        return asyncio.StreamReaderProtocol(stream_reader)

    transport, _ = await loop.connect_read_pipe(protocol_factory, pipe)
    line = await stream_reader.readline()
    print(line)
    transport.close()


def writer(write):
    os.write(write, b'Hello World\n')


if __name__ == "__main__":
    name_main()
        # sys.exit()
