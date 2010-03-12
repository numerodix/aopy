# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import submain

if __name__ == '__main__':
    print(submain.func(1))
    print(submain.Obj().meth('x'))


### TESTSPEC ###
"""
---- dec ---- func
1
---- dec ---- meth
x
"""
