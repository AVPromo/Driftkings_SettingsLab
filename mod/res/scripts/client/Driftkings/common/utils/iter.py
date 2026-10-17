# -*- coding: utf-8 -*-
__all__ = ('remDups',)

def remDups(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]
