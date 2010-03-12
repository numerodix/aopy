# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

#import aspects.mymetaclasses as mymetaclasses
#import aspects.mydecorators as mydecorators

#@mydecorators.dec
def func(x):
    return x

class Obj(object):
    #__metaclass__ = mymetaclasses.Meta

    ##@mydecorators.dec
    def meth(self, y):
        return y

if __name__ == '__main__':
    print func(1)
    print Obj().meth('x')


### TESTSPEC ###
"""
---- dec ---- func
1
---- dec ---- meth
x
"""
