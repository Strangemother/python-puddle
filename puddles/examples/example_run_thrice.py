import time

from puddles import raw, extras

def main():
    sigs = (
        (process_func, ),
        (process_func, (2,)),
        (process_func, (), {'timeout': 1})
    )

    return raw.run(sigs)
    # (1, 2, 3)


async def process_func(timeout=3):
    print('Process execution timeout:', timeout)
    await extras.async_sleep(timeout)
    return timeout


if __name__ == '__main__':
    res = main()
    print(res)

