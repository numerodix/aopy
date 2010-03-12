# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import modules.classes
import modules.functions

if __name__ == '__main__':
    print(modules.functions.func(1))
    print(modules.classes.Obj().meth('x'))


### TESTSPEC ###
"""
---- dec ---- func
1
---- dec ---- meth
x
"""
