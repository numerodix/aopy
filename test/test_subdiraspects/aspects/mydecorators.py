# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def dec(f):
    def new_f(*a, **k):
        print "---- dec ----", f.__name__
        return f(*a, **k)
    return new_f
