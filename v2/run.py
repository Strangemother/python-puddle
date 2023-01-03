import raw, asyncio, extras


def main():
    packs = (primary_proc_main, primary_proc_main, )
    raw.submit(items=packs)


def primary_proc_main(*a, **kw):
    print('primary_proc_main', a, kw)
    try:
        asyncio.run(extras.async_sleep_tick(1,*a, **kw))
    except KeyboardInterrupt:
        print('KB Kill',a)

if __name__ == '__main__':
    main()
