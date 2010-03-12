# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import compiler.ast as ast


class SimpleTreePPrinter(object):
    def node_name(self, node):
        return str(node.__class__).replace('compiler.ast.', '')

    def join_with(self, node, depth, sep):
        return sep.join([self.display(n, depth+2, sep) for n in node])

    def display(self, node, depth=0, sep=None):
        """This output is not! eval'able (and never will be) because ast.Node
        subclasses mangle the output from their internal representation.
        *sigh*"""
        sep_break = ",\n%s" % (depth*' ')
        if not sep:
            sep = ", "

        fmt = None
        if isinstance(node, list):
            fmt = "[%s]"
        if isinstance(node, tuple):
            fmt = "(%s)"
        if fmt:
            output = fmt % self.join_with(node, depth, sep_break)
#            output = fmt % self.join_with(node, depth, sep)
#            if depth+len(output) > 79:
#                output = fmt % self.join_with(node, depth, sep_break)
            return output
        if not isinstance(node, ast.Node):
            return repr(node)

        name = self.node_name(node)
        subs = node.getChildren()
        items = self.display(subs, depth+2)
        return "%s%s" % (name, items)
