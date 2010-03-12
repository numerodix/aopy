# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def new(func):
    def new_func(*args, **kw):
        print("New decorator")
        return func(*args, **kw)
    return new_func

def old(func):
    def new_func(*args, **kw):
        print("Old decorator")
        return func(*args, **kw)
    return new_func


#import myaspects

#@myaspects.injected
@new
def compute(x):
    """Compute fun exponents"""
    print("Function")
    return x**x

compute = old(compute)


if __name__ == "__main__":
    compute(4)


### TESTSPEC ###
"""
Old decorator
Injected decorator
New decorator
Function
"""
