import os
import sys

try:
    import win32api
except ImportError:
    print('win32api is not available')

try:
    import win32con
except ImportError:
    print('win32con is not available')

try:
    import win32process
except ImportError:
    print('win32process is not available')

import ctypes


def set_cores(core_ints, handle=None):
    return set_core(*set_core)


def set_core(*index, handle=None):
    # affinity mask is 2 ** core_int, == 2 ** 7 == 128
    handle = handle or win32_handle()
    return win32_set_handle_affinity(handle, cores_bit_mask(*index))

def cores_bit_mask(*core_ints):
    """Provide a list of process core integer ids, and return a bit mask
    representing the _enabled_ cores as one 0-255

        cores_bit_mask(1,3,6)
        74
    """
    return sum(tuple(map(lambda x: 2**x, core_ints)))


def ctypes_set_core(index=0):
    # affinity mask is 2 ** core_int, == 2 ** 7 == 128
    return set_handle_core(win32_handle().handle, 2**index)


def set_handle_core(handle:int, index=0):
    ctypes.windll.kernel32.SetProcessAffinityMask(handle, index)


def win32_set_handle_affinity(handle, mask):
    """Currently the working one.

    handle = the _new_ handle <PyHandle> from win32_handle
    mask = a bit mask of the CPU integer 2**{i}, e.g: i=5 == 2**5 == mask=32

        set_core(6)
        win32_set_handle_affinity(win32_handle(), 2**6)

    The thread executes on the target e.g. 6
    """
    win32process.SetProcessAffinityMask(handle, mask)

def get_cpu_affinity(handle=None):
    handle = handle or win32_handle()
    core, handle = win32process.GetProcessAffinityMask(handle)
    return core, handle

def ctypes_handle():
    handle = ctypes.windll.user32.GetForegroundWindow()
    return handle

def threadid(handle):
    return ctypes.windll.user32.GetWindowThreadProcessId(handle)


def win32_handle(pid=None):

    import win32con

    from . import win32api
    pid = pid or os.getpid()
    print('win32_handle', pid)
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    return handle

def wind32_getpid():
    return win32api.GetCurrentProcessId()

import time

def intense(seconds=4):
    print(f"Starting CPU intensive task now for 4 seconds on...", flush=True)
    t_end = time.perf_counter() + seconds
    while time.perf_counter() < t_end:
        pass
    print('done.')


def get_window_handle(parent=True, console=False):
    command = ctypes.windll.kernel32.GetConsoleWindow if console else ctypes.windll.user32.GetForegroundWindow
    if not parent:
        return command()

    #Find the parent windows until there are none left
    while True:
        try:
            parent = ctypes.windll.user32.GetParent(hwnd)
        except UnboundLocalError:
            hwnd = command()
        else:
            if parent:
                hwnd = parent
            else:
                break
    return hwnd


class Handle:

    win32 = staticmethod(win32_handle)

    ## I think these are not handle ids...
    ctypes = staticmethod(ctypes_handle)
    window = staticmethod(get_window_handle)

    @classmethod
    def console(cls):
        return cls.window(console=True)


def get_cores():
    return power_match(*get_cpu_affinity())


def power_match(a,b):
    """

        power_match( (2**6) + (2**2), 0)

    """
    print(a, b)
    r = range(0, 8)

    cores = ()

    for i in r:
        p = 2 ** i
        v = a & p
        if v == 0:
            continue

        cores += (i,)
        print(i, p, v)

    return cores
