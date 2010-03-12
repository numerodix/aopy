# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys
sys.path.append('../..')
import aopy

import aspects.cache.main
import aspects.logger.main


aspect = aopy.Aspect()
# invert order (here: inner->outer) because decorators are added from the top
aspect.add_decorator('main:func', aspects.logger.main.dec)
aspect.add_decorator('main:func', aspects.cache.main.dec)

__all__ = ['aspect']
