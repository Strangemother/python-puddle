import shadow

SHADOW_KEY = '__shadow.meta__'

meta = shadow.Shadow(_shadow_keystack=(SHADOW_KEY,))



def skey(k):
    return f'{SHADOW_KEY}.{k}'


def key_replace(head, key):
    # print('test', key, vars(head))
    return head.key_map.get(key, key)


def proc_process_meta(head, a, kw):
    # print('proc_process_meta', a, kw)
    # print(head.key_map)
    rkw = {}
    ra = ()
    for v in a:
        # ra += (v,)
        ra += (key_replace(head, v),)

    for k, v in kw.items():
        rkw[k] = key_replace(head, v)
    return ra, rkw
