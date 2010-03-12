# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys
sys.path.append('../..')
import aopy

import myaspects


aspect = aopy.Aspect()
aspect.add_property('main:Obj/att', 
    fget=myaspects._get, fset=myaspects._set, fdel=myaspects._del)

__all__ = ['aspect']
