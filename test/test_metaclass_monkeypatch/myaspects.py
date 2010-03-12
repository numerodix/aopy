# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import inspect
import types


def _get(self):
    print("++ Getter sees %s" % self._att)
    return self._att

def _set(self, value):
    print("++ Settter sees %s" % value)
    self._att = value

def _del(self):
    print("++ Deleter sees %s" % self._att)


def decorator(func):
    """Analyze arguments, perform function, report result"""
    def new_func(*args, **kw):
        print("** Entering function: %s" % func.__name__)

        (arg_names, varargs, kwargs, kw_defaults) = inspect.getargspec(func)

        print("  Received arguments:")
        for (e, pair) in enumerate(zip(args, arg_names)):
            (arg, arg_name) = pair
            arg_s = str(arg)
            # pretty print 'self' to avoid printing variable memory address
            if arg_name == "self":
                arg_s = "instance of class %s" % arg.__class__.__name__
            print("    %s) %s" % (e, arg_s))

        print("  Received keyword arguments:")
        for (k, v) in kw.items():
            print("    %s: %s" % (k, v))

        res = func(*args, **kw)

        print("  Returning result: %s" % res)

        return res
    return new_func


# manufacture phony __init__ wrapper
def initwrap(func):
    """The goal is to rebind all attributes through properties. However, this
    can't be done directly in the metaclass, because instance attributes
    (self.att) only get set when the instance calls self.__init__, after both
    __new__ and __init__ (recall that the __init__ in the metaclass is an
    altogether different method from __init__ in self) have been executed in 
    the metaclass.

    What we do instead is wrap self.__init__, and intercept this call just
    after the method has finished executing. By now we know that attributes
    initialized in __init__ have been set. We can now enumerate self's
    namespace to find the names of the attributes. Knowing this, we create a
    property for each one, and bind this with the attribute's name, but in the
    *class's* namespace, not the instance's (this is how properties work). To
    leave a "clean slate" we can also remove the attribute from the instance's
    namespace (although lookup will be superseded by the property).
    """
    def newinit(self, *args, **kw):
        print("--> This is phony init!")

        # call __init__
        res = func(self, *args, **kw)

        # __init__ has finished, let's wreak havoc!
        for (k, v) in self.__dict__.items():
            # we've found an attribute in self

            # delete it from self's dict
            delattr(self, k)

            # create a property and bind it with att's name, in
            # self.__class__'s dict
            setattr(self.__class__, k, property(fget=_get, fset=_set, fdel=_del))

            # restore att's value using the property
            setattr(self, k, v)

        return res
    newinit.__name__ = func.__name__
    return newinit


class Metaclass(type):
    def __new__(cls, name, bases, dct):
        for (k, v) in dct.items():
            if type(v) == types.FunctionType:

                if k == "__init__":
                    # decorate with phony init
                    dct[k] = initwrap(v)

                # decorate every function with decorator
                dct[k] = decorator(dct[k])

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(Metaclass, cls).__init__(name, bases, dct)

    
