# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

"""Mix in classes for path handling"""

import os
import sys


class File(object):

    def set_file(self, file):
        """Set file name in various forms

        >>> fileobj = File()
        >>> fileobj.file = "/path/to/file.ext"
        >>> fileobj.file
        '/path/to/file.ext'
        >>> fileobj.file_path
        '/path/to'
        >>> fileobj.file_name
        'file.ext'
        >>> fileobj.file_name_root
        'file'
        >>> fileobj.file_name_ext
        '.ext'
        """

        self._file = os.path.abspath(file)

        self._file_path = os.path.dirname(self._file)
        self._file_name = os.path.basename(self._file)

        (root, ext) = os.path.splitext(self.file_name)
        self._file_name_root = root
        self._file_name_ext = ext

    file = property(fset=set_file, fget=lambda self: self._file)
    file_path = property(fget=lambda self: self._file_path)
    file_name = property(fget=lambda self: self._file_name)
    file_name_root = property(fget=lambda self: self._file_name_root)
    file_name_ext = property(fget=lambda self: self._file_name_ext)

    def _print(self):
        print("file           : %s" % self.file)
        print("file_path      : %s" % self.file_path)
        print("file_name      : %s" % self.file_name)
        print("file_name_root : %s" % self.file_name_root)
        print("file_name_ext  : %s" % self.file_name_ext)

class Module(File):

    def get_pycfile(self):
        """Get module's pycfile

        >>> moduleobj = Module()
        >>> moduleobj.set_file("/path/to/main.py")
        >>> moduleobj.pycfile
        '/path/to/main.pyc'
        """

        return self.file + 'c'

    pycfile = property(fget=get_pycfile)

    def _print(self):
        File._print(self)
        print("pycfile        : %s" % self.pycfile)


def is_writable(file):
    """Check file and containing dir for write access

    1) Assume tempfile creation works on the system.
    2) Create a tempfile.
    3) Verify write access.

    >>> import tempfile
    >>> try:
    ...    fd = tempfile.NamedTemporaryFile(prefix=".doctest_")
    ...
    ...    # temp dir (/tmp) should be writable
    ...    is_writable(os.path.dirname(fd.name))
    ...
    ...    # tempfile should be writable
    ...    is_writable(fd.name)
    ... finally:
    ...    fd.close()
    True
    True
    """

    if os.path.exists(file):
        if os.access(file, os.W_OK):
            return True
    elif os.access(os.path.dirname(file), os.W_OK):
        return True

def try_import(module_name=None, module_file=None):
    """Import module by module name or file name, return module object"""
    assert module_name or module_file
    if module_name:
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
        modobj = __import__(module_name)
    elif module_file:
        m = Module()
        m.file = module_file
        if m.file_path not in sys.path:
            sys.path.append(m.file_path)
        modobj = __import__(m.file_name_root)
    return modobj


if __name__ == "__main__":
    import doctest
    doctest.testmod()
