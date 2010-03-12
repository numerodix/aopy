# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import compiler
import compiler.ast as ast
import os
import sys

from aspect import Aspect, Worklist
import astpp
import filepath
import visitors


class ModuleCompiler(compiler.pycodegen.Module, filepath.Module):
    def __init__(self, filename, basepath=None):
        self.filename = filename
        self.source = filename
        self.tree = None

        if basepath:
            base = os.path.commonprefix([self.file_path, basepath])
            localfile = self.file[1+len(base):]
            (self.local_name, _) = os.path.splitext(localfile)

    def _set_filename(self, value):
        self.file = value

    def _get_filename(self):
        return self.file

    filename = property(fget=_get_filename, fset=_set_filename)
    source = property(fget=_get_filename, fset=_set_filename)


    def get_tree(self):
        """Parse on demand"""
        if not self._tree:
            self.parse()
        return self._tree

    def _get_tree(self):
        return self.tree

    def set_tree(self, tree):
        self._tree = tree

    tree = property(fget=get_tree, fset=set_tree)

    def parse(self):
        tree = compiler.parse(open(self.file).read(), self.mode)
        compiler.misc.set_filename(self.file, tree)
        compiler.syntax.check(tree)
        self.tree = tree

    def display(self):
        print astpp.SimpleTreePPrinter().display(self.tree)
#        print astpp.TreePPrinter(self.file_name).display(self.tree)


    def find_names(self):
        namefinder = visitors.NameFinderVisitor()
        compiler.walk(self.tree, namefinder)
        return namefinder.get_names()

    def find_imports(self):
        namefinder = visitors.ImportFinderVisitor()
        compiler.walk(self.tree, namefinder)
        return namefinder.get_names()


    def transform(self, worklist):
        trans = visitors.TransformerVisitor.PHASE_TRANSFORM
        post = visitors.TransformerVisitor.PHASE_POST

        sys.stderr.write("Transforming module %s\n" % self.file)
        visitor = visitors.TransformerVisitor(trans, self.local_name, worklist)
        compiler.walk(self.tree, visitor)
        if visitor.matched_advices:
            worklist = visitor.matched_advices
            visitor = visitors.TransformerVisitor(post, self.local_name, worklist)
            compiler.walk(self.tree, visitor)
            compiler.syntax.check(self.tree)     # ?
            return True

    def writepyc(self, verbose=False):
        if verbose:
            self.display()
        self.compile(display=False)
        self.dump(open(self.pycfile, 'w'))


    def chase_imports(self):
        modules = set()
        queue = [self.file_name_root]
        for name in queue:
            try:
                modobj = filepath.try_import(module_name=name)
                file = getattr(modobj, '__file__', None)
                if not file:
                    sys.stderr.write("Module object %s missing __name__ att\n" % name)
                    raise Exception
                (base, _) = os.path.splitext(file)
                m = ModuleCompiler(base + '.py')
                if file not in (m.file, m.pycfile):
                    sys.stderr.write("Module cannot be parsed: %s\n" % file)
                    raise Exception
                if not os.path.exists(m.file):
                    sys.stderr.write("Module does not exist: %s\n" % m.file)
                    raise Exception
                if not filepath.is_writable(m.pycfile):
                    sys.stderr.write("Path cannot be written to: %s\n" % m.pycfile)
                else:
                    modules.add(m)
                found = m.find_imports()
                for f in found:
                    if f not in queue:
                        queue.append(f)
            except:
                raise
        return list(modules)

    def load_spec(self, file):
        spec = filepath.try_import(module_file=file)
        aspnames = (aspname for aspname in spec.__all__)
        aspects = (getattr(spec, aspname) for aspname in aspnames)
        return Worklist(*aspects)

    def find_modules(self, path):
        modules = []
        for (dir, dirs, files) in os.walk(path):
            for f in files:
                f = os.path.join(dir, f)
                (_, e) = os.path.splitext(f)
                if e == '.py':
                    pyc = f + 'c'
                    if not filepath.is_writable(pyc):
                        sys.stderr.write("Path cannot be written to: %s\n" % pyc)
                    else:
                        modules.append(f)
        modules = list(set(modules))
        return modules
