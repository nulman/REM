from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
del glob, dirname, basename, isfile, modules
__all__.remove('__init__')

graphtypes = {}
for item in __all__:
    mod = __import__('{}'.format(item,item),locals(),globals())
    #print type(mod)
    #print mod
    graphtypes.update(getattr(mod,item)().getparameters())
#print '__all__: {}'.format(__all__)    
#print graphtypes
 #   [{'Line': {'group-by': 'multiple', 'x-axis': 'single', 'y-axis': 'signle'}},{'Line2': {'group-by': 'multiple', 'x-axis': 'single', 'y-axis': 'signle'}}]
 #    {'Line': {'group-by': 'multiple', 'x-axis': 'single', 'y-axis': 'signle'}, 'Line2': {'group-by': 'multiple', 'x-axis': 'single', 'y-axis': 'signle'}}