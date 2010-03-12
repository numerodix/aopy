# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

# Pass 1: This is what the aspect actually does
## Pass 2: This is what the metaclass does programmatically

#import myaspects

class Class(object):
    #__metaclass__ = myaspects.Metaclass

    ##@myaspects.decorator
    ##@myaspects.initwrap
    def __init__(self):
        self.att = 1

    ##@myaspects.decorator
    def compute(self, x, y=None):
        if y:
            return x**y
        return x**x

    ##att = property(fget=myaspects._get, fset=myaspects._set, fdel=myaspects._del)

c = Class()

print(c.compute(4))
print(c.compute(4, y=3))

print(c.att)
c.att = 2
print(c.att)
del c.att

### TESTSPEC ###
"""
** Entering function: __init__
  Received arguments:
    0) instance of class Class
  Received keyword arguments:
--> This is phony init!
++ Settter sees 1
  Returning result: None
** Entering function: compute
  Received arguments:
    0) instance of class Class
    1) 4
  Received keyword arguments:
  Returning result: 256
256
** Entering function: compute
  Received arguments:
    0) instance of class Class
    1) 4
  Received keyword arguments:
    y: 3
  Returning result: 64
64
++ Getter sees 1
1
++ Settter sees 2
++ Getter sees 2
2
++ Deleter sees 2
"""
