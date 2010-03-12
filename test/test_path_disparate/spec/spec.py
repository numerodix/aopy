import sys
sys.path.append('../aspects')
import myaspects

import aopy
aspect = aopy.Aspect()
aspect.add_decorator("", myaspects.decorator)

__all__ = ["aspect"]
