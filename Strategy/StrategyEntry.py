import logging
import traceback

from os import sys, path
from datetime import datetime
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.DataUtility import DataUtility
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.DataUtility import DataUtility
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
finally:
    logger = logging.getLogger('')


class StrategyEntry:
    def __init__(self, strategy_plugin: PluginManager):
        self.__strategy_plugin = strategy_plugin

    def get_plugin_manager(self) -> PluginManager:
        return self.__strategy_plugin

    # ------------------------------------------------------------------------------------------------------------------

    def run_strategy(self, uri: str):
        plugins = self.get_plugin_manager().find_module_has_capacity(uri)
        for plugin in plugins:
            df = self.get_plugin_manager().execute_module_function(plugin, 'query', {})
            if df is not None and isinstance(df, pd.DataFrame) and len(df) > 0:
                return df
        return None


# ----------------------------------------------------------------------------------------------------------------------
#                                                         Test
# ----------------------------------------------------------------------------------------------------------------------

def test_entry():
    pass


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    test_entry()

    # If program reaches here, all test passed.
    print('All test passed.')


# ------------------------------------------------- Exception Handling -------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass

