import logging
import traceback

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common
    from DataHub.DataHubEntry import DataHubEntry
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common
    from DataHub.DataHubEntry import DataHubEntry
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
finally:
    logger = logging.getLogger('')


class StrategyEntry:
    def __init__(self, strategy_plugin: PluginManager, data_hub: DataHubEntry):
        self.__data_hub = data_hub
        self.__strategy_plugin = strategy_plugin

    def get_plugin_manager(self) -> PluginManager:
        return self.__strategy_plugin

    # ------------------------------------------------------------------------------------------------------------------

    def strategy_prob(self) -> [dict]:
        return self.get_plugin_manager().execute_module_function(
            self.get_plugin_manager().all_modules(), 'plugin_prob', {})

    def run_strategy(self, securities: [str], methods: [str]):
        return self.get_plugin_manager().execute_module_function(
            self.get_plugin_manager().all_modules(), 'plugin_prob', {
                'securities': securities,
                'methods': methods,
                'data_hub': self.__data_hub
            })


# ----------------------------------------------------------------------------------------------------------------------
#                                                         Test
# ----------------------------------------------------------------------------------------------------------------------

def __prepare_instance() -> StrategyEntry:
    plugin_mgr = PluginManager(path.join(root_path, 'Analyzer'))
    plugin_mgr.refresh()
    return StrategyEntry(plugin_mgr, None)


def test_analyzer_prob():
    se = __prepare_instance()
    probs = se.strategy_prob()
    print(probs)


def test_score():
    se = __prepare_instance()
    se.run_strategy(
        [''],
        ['5d19927a-2ab1-11ea-aee4-eb8a702e7495', 'bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4'])


def test_entry():
    test_analyzer_prob()


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

