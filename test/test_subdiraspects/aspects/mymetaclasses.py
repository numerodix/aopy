# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import mydecorators

class Meta(type):
    def __new__(cls, name, bases, dct):
        for (k, v) in dct.items():
            import types
            if type(v) == types.FunctionType:
                dct[k] = mydecorators.dec(v)
        return type.__new__(cls, name, bases, dct)
