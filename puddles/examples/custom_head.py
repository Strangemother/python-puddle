import puddles

def main():
    """run the custom head 10 times, but on 5 open cores. sum the result."""

    packs = (
        func,
        puddles.count(2, func),
        puddles.count(7, func),
    )

    res = puddles.run(
        items=packs,
        ## No count opens n=len(packs)
        ## less than {n} will execute {count} until a thread death,
        ## spawning a new task until exausted.
        count=5,

        # don't run the given func, rather assign it to an
        # 'accepting' func to offload execution.
        # head_class=Doublnator,
        head_class='__main__.Doublnator',
        # head_class='custom_head.Doublnator',
        # head_class='examples.custom_head.Doublnator',
        # head_class='puddles.head.InfoHead',
    )

    return sum(res)


def func(*a, **kw):
    print('proc func', a, kw)
    return 1


class Doublnator(puddles.head.InfoHead):
    """The Doublnator runs the internal function twice."""
    def setup(self):
        """A hook for process starts"""
        print('New Process', self.kwargs)

    def live(self, *a, **kw):
        """run twice for no reason:"""
        va = self.run_func(*a, **kw)
        vb = self.run_func(*a, **kw)
        return va + vb


if __name__ == '__main__':
    result = main()
    assert result == 20
    print(result)
