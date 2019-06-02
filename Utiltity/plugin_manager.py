import os
import traceback
from inspect import getmembers, isfunction


"""
A plug-in module should include following functions:
    plugin_prob() -> dict : Includes 'plugin name', 'plugin_version'
    plugin_capacity() -> [str] : Lists the functions that module supports
    
    The function and parameter should follow the function in DataHub
"""


def function_exists(obj, function_name: str) -> bool:
    try:
        return callable(getattr(obj, function_name))
    except Exception as e:
        print("Check callable fail.!")
        print('Error =>', e)
        return False
    finally:
        pass


class PluginManager:
    def __init__(self, plugin_path: str):
        self.__path = plugin_path
        self.__plugins = []

    def refresh(self):
        """
        Refresh plugin list immediately. You should call this function if any updates to the plug-in folder.
        :return: None
        """
        plugin_list = []
        module_files = os.listdir(self.__path)
        for file_name in module_files:
            if not file_name.endswith('.py') or file_name.startswith('_') or file_name.startswith('.'):
                continue
            plugin_name = os.path.splitext(file_name)[0]
            plugin = __import__(self.__path + '.' + plugin_name, fromlist=[plugin_name])
            if not function_exists(plugin, 'plugin_prob') or not function_exists(plugin, 'plugin_capacity'):
                continue
            plugin_list = [(file_name, plugin)]
        self.__plugins = plugin_list

    def get_support_module(self, function: str) -> [object]:
        """
        Give a function. Finds the module that includes this function.
        :param function: The function you want to support.
        :return: The module list that supports this function.
        """
        module_list = []
        for plugin in self.__plugins:
            functions = self.__safe_execute(plugin, 'plugin_capacity')
            if isinstance(functions, list) and function in functions:
                module_list.append(plugin)
        return module_list

    def get_module_functions(self, module: object) -> [str]:
        """
        Get function of a module.
        :param module: The module that you want to check. Not support list.
        :return: The function list of this module
        """
        # getmembers returns a list of (object_name, object_type) tuples.
        functions_list = [o for o in getmembers(module) if isfunction(o[1])]
        return functions_list

    def execute_module_function(self, modules: object or [object], function: str,
                                end_if_success: bool = True) -> object or [object]:
        """
        Execute function of Module
        :param modules: The module that you want to execute its function. Can be an object or a list of object
        :param function: The function you want to invoke
        :param end_if_success: If True, this function will return at the first successful invoking.
        :return: The object that the invoking function returns, it will be a list if the modules param is a list.
                 Includes None return.
        """
        if isinstance(modules, object):
            modules = [modules]
        result_list = []
        for module in modules:
            result_obj = self.__safe_execute(module, function)
            if result_obj is not None and end_if_success:
                return result_obj
            result_list.append(result_obj)
        return result_list

    # --------------------------------------- Execute ---------------------------------------

    def __safe_execute(self, module: object, function: str, *args) -> object:
        try:
            func = getattr(module, function)
            return_obj = func(*args)
        except Exception as e:
            return_obj = None
            print("Function run fail.")
            print('Error =>', e)
            print('Error =>', traceback.format_exc())
        finally:
            pass
        return return_obj








