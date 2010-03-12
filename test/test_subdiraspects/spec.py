# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys
sys.path.append('../..')
import aopy

import myaspects


aspect = aopy.Aspect()
aspect.add_decorator('main:func', myaspects.aspects.mydecorators.dec)
aspect.add_metaclass('main:Obj', myaspects.aspects.mymetaclasses.Meta)

__all__ = ['aspect']
