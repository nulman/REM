"""
@author Liran Funaro <funaro@cs.technion.ac.il>
"""

import os
import imp
import sys
import glob
import types

class PluginManager:
    PLUGIN_PACKAGE = "rem_plugins"

    def __init__(self, plugins_path="plugins"):
        self.__plugins_path = plugins_path
        self.__plugins_search_term = os.path.join(self.__plugins_path, "*.py")

        plugins_package = types.ModuleType(self.PLUGIN_PACKAGE)
        plugins_package.__path__ = [plugins_path]
        sys.modules[self.PLUGIN_PACKAGE] = plugins_package

        self.reload_plugins()

    def reload_plugins(self):
        self.__plugins_map = {}
        self.__plugins_parameters = {}

        for file_path, name in self.__iter_plugins__():
            self.__load_plugin__(file_path, name)

    def get_plugin(self, desc):
        name = self.__plugins_map[desc]
        module_name = self.__plugin_module_name(name)
        return sys.modules[module_name]

    def plugins_parameters(self):
        return self.__plugins_parameters.copy()

    def get_plugin_parameters(self, name):
        return self.__plugins_parameters[name]

    def plugins_images(self):
        return {p: self.get_plugin(p).image_path() for p in self.__plugins_map}

    def __getitem__(self, item):
        return self.get_plugin(item)

    ############################################################################
    # Helper functions
    ############################################################################

    @classmethod
    def __plugin_module_name(cls, name):
        return "%s.%s" % (cls.PLUGIN_PACKAGE, name)

    def __iter_plugins__(self):
        for f in glob.glob(self.__plugins_search_term):
            base = os.path.basename(f)
            name, ext = os.path.splitext(base)
            yield f, name

    def __load_plugin__(self, file_path, name):
        try:
            module_name = self.__plugin_module_name(name)
            m = imp.load_source(module_name, file_path)
            desc = m.description()
            params = m.parameters()
            self.__plugins_map[desc] = name
            self.__plugins_parameters[desc] = params
        except Exception as e:
            print "[ERROR] Can't load plugin", name, ":", e # Should log
        else:
            print "[SUCCESS] Plugin", name, "loaded" # Should log

# Unit test
if __name__ == "__main__":
    p = PluginManager("plugins")

    print "Parameters:"
    print "==========================================================="
    import json
    print json.dumps(p.plugins_parameters(), indent=4)