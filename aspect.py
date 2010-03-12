# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

"""Both the Aspect and Worklist types are containers for Advice objects. Aspect
is the public API to define transformations in semantically meaningful ways.
Worklists are used internally to aggregate advices from all the given aspects
and provide methods for access and filtering."""

import os

import filepath


def hash_items(*args):
    return reduce(long.__add__, map(long, map(hash, args)))


class Object(object):
    def __init__(self, obj):
        if not obj:
            self = None
            return

        self.modulename = obj.__module__    # original name
        self.set_default_module_name()
        self.objname = obj.__name__

        try:
            path = filepath.try_import(module_name=self.modulename).__file__
        except ImportError:
            raise   # XXX capitulate?
        self.file = os.path.abspath(path)

    def set_default_module_name(self):
        module = '.'.join(self.modulename.split('.')[-1:])
        self.module = module                # mangled name

    def __hash__(self):
        try:
            return hash_items(self.modulename, self.module, self.objname)
        except AttributeError:
            return 0


class Advice(object):
    def __init__(self, pattern, inj_obj):
        self.pattern = pattern
        self.object = Object(inj_obj)

    def __hash__(self):
        """Assist in duplicate detection"""
        return hash_items(*tuple([self.pattern] + [obj for obj in self]))

    def __iter__(self):
        return (obj for obj in (self.object,))

class DecoratorAdvice(Advice): pass
class MetaclassAdvice(Advice): pass
class PropertyAdvice(Advice):
    def __init__(self, pattern, fget, fset, fdel):
        self.pattern = pattern
        self.fget = Object(fget)
        self.fset = Object(fset)
        self.fdel = Object(fdel)

    def __iter__(self):
        return (obj for obj in (self.fget, self.fset, self.fdel))


class Aspect(object):
    """This class is the public API to aopy"""
    def __init__(self):
        self.worklist = []

    def add_decorator(self, pattern, obj):
        adv = DecoratorAdvice(pattern, obj)
        self.worklist.append(adv)

    def add_metaclass(self, pattern, obj):
        adv = MetaclassAdvice(pattern, obj)
        self.worklist.append(adv)

    def add_property(self, pattern, fget=None, fset=None, fdel=None):
        adv = PropertyAdvice(pattern, fget, fset, fdel)
        self.worklist.append(adv)

    @classmethod
    def iter(cls, *aspects):
        """Enumerate all advices from worklists in aspects. Should be possible in
        a list comprehension???"""
        for aspect in aspects:
            for advice in aspect.worklist:
                yield advice

    @classmethod
    def join(cls, *aspects):
        """Aggregate advices and filter out duplicates (order preserving)."""
        seen = {}
        items = []
        for item in cls.iter(*aspects):
            if item not in seen:
                items.append(item)
                seen[item] = None
        return items


class Worklist(object):
    def __init__(self, *aspects):
        self.advices = Aspect.join(*aspects)

    def append(self, advice):
        self.advices.append(advice)

    def __len__(self):
        """Allow instances to be used as checks in if statements based on the
        length of the container."""
        return len(self.advices)


    def get_module_paths(self):
        objs = []
        for adv in self.advices:
            for obj in adv:
                file = getattr(obj, 'file', None)
                if file:
                    m = filepath.Module()
                    m.file = file
                    # appears completely broken
                    #path = os.sep.join(m.file_path.split(os.sep)[:-1]) # XXX ??
                    path = m.file_path
                    objs.append(path)
        return list(set([obj for obj in objs]))

    def get_modules(self):
        objs = []
        for adv in self.advices:
            for obj in adv:
                if hasattr(obj, 'module'):
                    objs.append(obj)
        return list(set([(obj.modulename, obj.module) for obj in objs]))

    def get_decorators(self):
        return [adv for adv in self.advices if isinstance(adv, DecoratorAdvice)]

    def get_metaclasses(self):
        return [adv for adv in self.advices if isinstance(adv, MetaclassAdvice)]

    def get_properties(self):
        return [adv for adv in self.advices if isinstance(adv, PropertyAdvice)]


    def mangle_modulenames(self, namelist):
        # find non null objects
        objs = []
        for advice in self.advices:
            for obj in advice:
                if hash(obj) != 0:
                    objs.append(obj)

        # hash by file,modulename to group by distinct files
        index = {}
        for obj in objs:
            index[obj.file + obj.modulename] = obj.module

        # mangle to produce uniques
        for e in index:
            while True:
                if index[e] in namelist:
                    index[e] = index[e] + '_'
                else:
                    namelist.append(index[e])
                    break

        # assign mangled names
        for obj in objs:
            obj.module = index[obj.file + obj.modulename]

