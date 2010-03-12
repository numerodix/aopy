# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def injected(func):
    def new_func(*args, **kwargs):
        print("Injected decorator")
        return func(*args, **kwargs)
    return new_func
