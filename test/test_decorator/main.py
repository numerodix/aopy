# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

#import myaspects

#@myaspects.decorator
def compute(x):
    """Compute fun exponents"""
    return x**x

print("Function name: %s" % compute.__name__)
print("Function doc: %s" % compute.__doc__)
print("Function module: %s" % compute.__module__)
print("Function dict: %s" % compute.__dict__)
print(compute(4))


### TESTSPEC ###
"""
Function name: compute
Function doc: Compute fun exponents
Function module: __main__
Function dict: {}
Received arguments: (4,) {}
Returning result: 256
256
"""
