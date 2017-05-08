'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>
'''

from os.path import dirname, basename, isfile, join as join_path
from pyclbr import readmodule
import glob
import traceback

modules = glob.glob(join_path(dirname(__file__),"*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
__all__.remove('__init__')
try:
    #template is the reference module, it should not be used directly
    __all__.remove('template')
except ValueError:
    pass

graphtypes = {}
module_to_class = {}
for item in __all__:
    try:
        class_name = readmodule('{}.{}'.format(basename(dirname(__file__)),item)).keys()[0]
        mod = __import__('{}'.format(item),locals(),globals())
    except ImportError as e:
        print e
        print 'The module file must contain a class with the same name as the module.\nskipping module {}'.format(item)
        continue
    try:
        current_class = getattr(mod,class_name)
        module_to_class[mod.__name__[mod.__name__.index('.')+1:]] = current_class.__name__
        #self.__class__.__name__
        graphtypes.update(current_class().getparameters())
    except AttributeError as e:
        print e
        print "make sure your plugin is well defined! things are case sensetive!"
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print traceback.format_exc()
        exit
del glob, dirname, basename, isfile, modules, readmodule, item
