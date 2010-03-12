# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

#import myaspects

class Obj(object):
    def __init__(self):
        self.att = 1

    #att = property(fget=myaspects._get, fset=myaspects._set, fdel=myaspects._del)

if __name__ == '__main__':
    obj = Obj()
    print(obj.att)
    obj.att = 2
    print(obj.att)
    del obj.att

### TESTSPEC ###
"""
++ Settter sees 1
++ Getter sees 1
1
++ Settter sees 2
++ Getter sees 2
2
++ Deleter sees 2
"""
