# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import compiler
import compiler.ast as ast
import compiler.consts as consts
import functools
import re
import sys

import aspect


def walkresumer(f):
    @functools.wraps(f)
    def new_f(self, node, *args):
        f(self, node, *args)
        self.resumewalk(node, *args)
    return new_f

class KeepWalkingMeta(type):
    def __new__(cls, name, bases, dct):
        for (k, v) in dct.items():
            import re, types
            if (type(v) == types.FunctionType and
                re.match("visit[a-zA-Z]+", k)):
                dct[k] = walkresumer(v)
        return type.__new__(cls, name, bases, dct)

class NullMeta(KeepWalkingMeta):
    "Can only override meta with a subclass of the metaclass"
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)


class AbstractVisitor(object):
    'Metaclass adds call to self.resumewalk at the end of every visit* method'
    __metaclass__ = KeepWalkingMeta
    def resumewalk(self, node, *args):
        'derive from compiler.visitor.ASTVisitor.default'
        for child in node.getChildNodes():
            self.visit(child, *args)


class NameFinderVisitor(AbstractVisitor):
    """Collect all the names/symbols in the tree that will be affected by
    introducing new bindings in a source transformation"""
    def __init__(self):
        self.names = {}

    def get_names(self):
        return self.names.keys()

    def visitAssName(self, node, *args):
        self.names[node.name] = None

    def visitClass(self, node, *args):
        self.names[node.name] = None

    def visitFrom(self, node, *args):
        self.names[node.modname] = None
        for name in node.names:
            self.names[name] = None

    def visitFunction(self, node, *args):
        self.names[node.name] = None
        for name in node.argnames:
            self.names[name] = None

    def visitImport(self, node, *args):
        for (name, asname) in node.names:
            self.names[name] = None
            if asname:
                self.names[asname] = None

    def visitGlobal(self, node, *args):
        for name in node.names:
            self.names[name] = None

    def visitKeyword(self, node, *args):
        self.names[node.name] = None

    def visitName(self, node, *args):
        self.names[node.name] = None


class ImportFinderVisitor(AbstractVisitor):
    "Find all [statically] imported modules"
    def __init__(self):
        self.names = {}

    def get_names(self):
        return self.names.keys()

    def visitImport(self, node, *args):
        for (name, asname) in node.getChildren()[0]:
            self.names[name] = None

    def visitFrom(self, node, *args):
        self.names[node.modname] = None


class TransformerVisitor(AbstractVisitor):
    """The transformer operates in two distinct phases. The transform phase
    matches advice patterns against pathspecs and performs transformations
    accordingly. However, these patterns are matched in the course of
    traversing the tree, so there is no way of knowing in advance whether a
    given module will match any of the advices. If it does not, it should not be
    touched. Therefore, imports are injected in a second phase based on the
    matches found in the transform phase."""

    __metaclass__ = NullMeta    # define our own decorators

    PHASE_TRANSFORM = 1
    PHASE_POST = 2

    def __init__(self, phase, localname, worklist, *a, **kw):
        self.phase = phase
        self.pathspec = localname + ':'
        self.worklist = worklist
        self.matched_advices = aspect.Worklist()
        AbstractVisitor.__init__(self, *a, **kw)


    ## Decorators

    def post_transform_walkresumer(f):
        """Only dispatch call in post transform mode."""
        @functools.wraps(f)
        def new_f(self, node, *args):
            if self.phase == self.PHASE_POST:
                f(self, node, *args)
            self.resumewalk(node, *args)
        return new_f

    def transform_walkresumer(f):
        """Intercept calls to functions this decorator is applied to when in
        post transform phase, thus omitting any transformation rules.
        Otherwise, advance the pathspec and pass it to the visit* function."""
        @functools.wraps(f)
        def new_f(self, node, *args):
            if self.phase == self.PHASE_TRANSFORM:
                args, pathspec = self.args_append(args, node)
                f(self, pathspec, node, *args)
            self.resumewalk(node, *args)
        return new_f

    def args_append(self, args, node):
        name = node.name
        pathspec = self.pathspec
        if name:
            if args:
                (pathspec, ) = args
                pathspec += '/' + name
            else:
                pathspec += name
        return (pathspec, ), pathspec


    ## Visit methods

    def match(self, advice, pathspec):
        if re.match(advice.pattern, pathspec):
            sys.stderr.write("Pattern matched: %s on %s\n" % (advice.pattern, pathspec))
            self.matched_advices.append(advice)
            return True
        sys.stderr.write("Pattern failed: %s on %s\n" % (advice.pattern, pathspec))

    @transform_walkresumer
    def visitClass(self, pathspec, node, *args):
        for advice in self.worklist.get_metaclasses():
            if self.match(advice, pathspec):
                self.set_metaclass(node, advice)

        # XXX inelegant, to put it mildly
        for advice in self.worklist.get_properties():
            for f in self.find_items_in_stmt(node, ast.Function):
                if self.is_instancemethod(node, f.name) and len(f.argnames) > 0:
                    self_name = f.argnames[0]
                    for ass in self.find_items_in_stmt(f, ast.Assign):
                        for assattr in ass:
                            if isinstance(assattr, ast.AssAttr):
                                pathspec += '/' + assattr.attrname
                                if isinstance(assattr.expr, ast.Name):
                                    if assattr.expr.name == self_name:
                                        if self.match(advice, pathspec):
                                            self.set_property(node, assattr.attrname, advice)

    @transform_walkresumer
    def visitFunction(self, pathspec, node, *args):
        for advice in self.worklist.get_decorators():
            if self.match(advice, pathspec):
                self.add_decorator(node, advice)

    @post_transform_walkresumer
    def visitModule(self, node, *args):
        mods = self.worklist.get_modules()
        paths = self.worklist.get_module_paths()
        self.add_imports(node, paths, mods)


    ## Mutation methods

    def add_imports(self, module, paths, mods):
        assert isinstance(module, ast.Module)
        body = module.node
        stmts = list(body.getChildNodes())

        # Add imports to injection modules
        for m in mods:
            stmts.insert(0, ast.Import([m]))

        # Add paths to modules
        """
        import sys
        for path in paths:
            if path not in sys.path:
                sys.path.append(path)
        """
        paths_node = map(ast.Const, paths)

        append = ast.Getattr(ast.Getattr(ast.Name('sys'), 'path'), 'append')
        call = ast.Discard(ast.CallFunc(append, [ast.Name('path')], None, None))
        sys_path = ast.Getattr(ast.Name('sys'), 'path')
        compare = ast.Compare(ast.Name('path'), [('not in', sys_path)])
        if_node = ast.If([(compare, ast.Stmt([call]))], None)
        assname = ast.AssName('path', consts.OP_ASSIGN)
        for_node = ast.For(assname, ast.Tuple(paths_node), ast.Stmt([if_node]), None)
        stmts.insert(0, for_node)

        imp_sys = ast.Import([('sys', None)])
        stmts.insert(0, imp_sys)

        module.node = ast.Stmt(stmts)

    def add_decorator(self, func, dec_advice):
        'Wraps decorator around existing (decs+func)'
        assert isinstance(func, ast.Function)
        assert isinstance(dec_advice, aspect.DecoratorAdvice)
        module_node = self.get_getattr(dec_advice.object.module)
        decorator = dec_advice.object.objname

        dec = ast.Getattr(module_node, decorator)
        func_decs = []
        if func.decorators:
            func_decs = list(func.decorators.getChildNodes())
        func_decs.insert(0, dec)
        func.decorators = ast.Decorators(func_decs)

    def set_metaclass(self, cl, meta_advice):
        'Overrides existing metaclass if set'
        assert isinstance(cl, ast.Class)
        assert isinstance(meta_advice, aspect.MetaclassAdvice)
        module_node = self.get_getattr(meta_advice.object.module)
        metaclass = meta_advice.object.objname

        # kill existing metaclass
        stmts = list(cl.code.getChildNodes())
        for st in stmts:
            if isinstance(st, ast.Assign):
                namenode = st.getChildNodes()[0]
                if isinstance(namenode, ast.AssName):
                    name = namenode.getChildNodes()[0]
                    if name == '__metaclass__':
                        stmts.remove(st)

        metakey = ast.AssName('__metaclass__', consts.OP_ASSIGN)
        metaval = ast.Getattr(module_node, metaclass)
        metast = ast.Assign([metakey], metaval)
        stmts.insert(0, metast)
        cl.code = ast.Stmt(stmts)

    def set_property(self, cl, name, advice):
        assert isinstance(cl, ast.Class)
        stmts = list(cl.code.getChildNodes())

        # kill existing property on this name
        for node in stmts:
            if isinstance(node, ast.Assign):
                for assname in node.getChildNodes():
                    if isinstance(assname, ast.AssName):
                        if assname.name == name:
                            stmts.remove(node)

        pairs = []
        for f_label in ('fget', 'fset', 'fdel'):
            f_name = getattr(getattr(advice, f_label), 'objname', None)
            module = getattr(getattr(advice, f_label), 'module', None)
            if f_name and module:
                module_node = self.get_getattr(module)
                n = ast.Getattr(module_node, f_name)
                pairs.append((ast.Keyword(f_label, n)))

        metakey = ast.AssName(name, consts.OP_ASSIGN)
        prop = ast.Name('property')
        metaval = ast.CallFunc(prop, pairs)
        metast = ast.Assign([metakey], metaval)
        stmts.append(metast)
        cl.code = ast.Stmt(stmts)


    ## Construction methods

    def get_getattr(self, modulepath):
        assert isinstance(modulepath, str)
        items = modulepath.split('.')
        if len(items) == 1:
            return ast.Name(items[0])
        else:
            return ast.Getattr(self.get_getattr('.'.join(items[:-1])), items[-1])

    ## Querying methods

    def is_instancemethod(self, cls, f_name):
        assert isinstance(cls, ast.Class)
        decs = ('classmethod', 'staticmethod')

        # decorator syntax
        for f in self.find_items_in_stmt(cls, ast.Function):
            if f.name == f_name and f.decorators:
                for dec in f.decorators:
                    if isinstance(dec, ast.Name):
                        if dec.name in decs:
                            return False

        # class attribute assignment
        for ass in self.find_items_in_stmt(cls, ast.Assign):
            assname, callfunc = None, None
            for n in ass:
                if isinstance(n, ast.AssName):
                    assname = n
                elif isinstance(n, ast.CallFunc):
                    callfunc = n

            if assname and callfunc:
                if assname.name == f_name:
                    callable_name = (n for n in callfunc).next()
                    if callable_name.name in decs:
                        return False

        return True

    def find_items_in_stmt(self, node, astnode):
        for n in node.getChildNodes():
            if isinstance(n, ast.Stmt):
                for child in n.getChildNodes():
                    if isinstance(child, astnode):
                        yield child
