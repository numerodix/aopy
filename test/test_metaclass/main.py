# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

#import myaspects

class Class(object):
    #__metaclass__ = myaspects.Metaclass
    pass

c = Class()

cls = c.__class__
clsname = cls.__name__
meta = c.__class__.__class__
metaname = meta.__name__

print("What is my class name?")
print("  c.__class__.__name__ ? %s" % (clsname))

print("What is my metaclass's name?")
print("  c.__class__.__class__.__name__ ? %s" % (metaname))

print("Is my class an instance of my metaclass?")
print("  isinstance(%s, %s) ? %s" %
      (clsname, metaname, isinstance(cls, meta)))

print("Is my class derived from object?")
print("  %s in %s.__bases__ ? %s" %
      (object.__name__, clsname, object in cls.__bases__))

print("Is my metaclass derived from type?")
print("  %s in %s.__bases__ ? %s" %
      (type.__name__, metaname, type in meta.__bases__))


### TESTSPEC ###
"""
Working: Creating class 'Class' from metaclass 'Metaclass'
Working: Intializing class 'Class' from metaclass 'Metaclass'
What is my class name?
  c.__class__.__name__ ? Class
What is my metaclass's name?
  c.__class__.__class__.__name__ ? Metaclass
Is my class an instance of my metaclass?
  isinstance(Class, Metaclass) ? True
Is my class derived from object?
  object in Class.__bases__ ? True
Is my metaclass derived from type?
  type in Metaclass.__bases__ ? True
"""
