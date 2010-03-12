# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

class Metaclass(type):
    def __new__(cls, name, bases, dct):
        print("Working: Creating class '%s' from metaclass '%s'" %\
              (name, cls.__name__))
        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        print("Working: Intializing class '%s' from metaclass '%s'" %\
              (name, cls.__class__.__name__))
        super(Metaclass, cls).__init__(name, bases, dct)
