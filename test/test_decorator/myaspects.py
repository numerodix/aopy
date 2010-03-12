# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def decorator(func):
    def new_func(*args, **kwargs):
        print("Received arguments: %s %s" % (args, kwargs))
        res = func(*args, **kwargs)
        print("Returning result: %s" % res)
        return res

    # Make sure attributes are preserved, so the function looks as if it hadn't
    # been touched
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__module__ = func.__module__
    new_func.__dict__.update(func.__dict__)

    return new_func
