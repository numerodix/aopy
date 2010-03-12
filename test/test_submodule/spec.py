# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys
sys.path.append('../..')
import aopy

import myaspects

aspect = aopy.Aspect()
aspect.add_decorator('submain:func', myaspects.dec)
aspect.add_metaclass('submain:Obj', myaspects.Meta)

__all__ = ['aspect']
