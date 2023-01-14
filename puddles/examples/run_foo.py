"""In this example we open 3 cores, and
"""

import puddles
from puddles.cpu import get_cores, intense

def cpu_core(*a, **opts):
    cores = get_cores()
    print('Open core', a, opts, cores)
    intense(2)
    return cores


def main():
    items = (
        puddles.count(3, cpu_core, 'star', elk='rep'),
    )
    return puddles.run(items, 2, foo='bar')


if __name__ == '__main__':
    res = main()
    print(res)
