# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def _get(self):
    print("++ Getter sees %s" % self._att)
    return self._att                      

def _set(self, value):
    print("++ Settter sees %s" % value)
    self._att = value                  

def _del(self):
    print("++ Deleter sees %s" % self._att)
