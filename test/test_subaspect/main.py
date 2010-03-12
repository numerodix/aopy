# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

#import mysubaspects

#@mysubaspects.dec
def func(x):
    return x

class Obj(object):
    #__metaclass__ = mysubaspects.Meta

    ##@mysubaspects.dec
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
