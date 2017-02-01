from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
del glob, dirname, basename, isfile, modules
__all__.remove('__init__')
try:
    #template is the reference module, it should not be used directly
    __all__.remove('template')
except ValueError:
    pass

graphtypes = {}
for item in __all__:
    try:
        mod = __import__('{}'.format(item,item),locals(),globals())
    except ImportError as e:
        print e
        print 'The module file must contain a class with the same name as the module.\nskipping module {}'.format(item)
        continue

    graphtypes.update(getattr(mod,item)().getparameters())
