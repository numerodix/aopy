# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def dec(func):
    def new_func(*args, **kw):
        print("Log this")
        return func(*args, **kw)
    return new_func
