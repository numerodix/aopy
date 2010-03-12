# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys
sys.path.append('../..')
import aopy

import myaspects


aspect = aopy.Aspect()
aspect.add_decorator('main:func', myaspects.mysubaspects.dec)
aspect.add_metaclass('main:Obj', myaspects.mysubaspects.Meta)

__all__ = ['aspect']
