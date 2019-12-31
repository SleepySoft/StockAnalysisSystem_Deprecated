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
            self.get_plugin_manager().all_modules(), 'analysis', {
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
    result = se.run_strategy(
        ['600001.SSZ', '70000004.SESZ'],
        ['5d19927a-2ab1-11ea-aee4-eb8a702e7495', 'bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4'])
    assert result[0].method == '5d19927a-2ab1-11ea-aee4-eb8a702e7495' and result[0].result == 1
    assert result[1].method == 'bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4' and result[1].result == 9
    assert result[2].method == '5d19927a-2ab1-11ea-aee4-eb8a702e7495' and result[2].result == 4
    assert result[3].method == 'bc74b6fa-2ab1-11ea-8b94-03e35eea3ca4' and result[3].result == 6


def test_inclusive():
    se = __prepare_instance()
    result = se.run_strategy(
        ['300008.SSZ', '00000005.SESZ'],
        ['6b23435c-2ab1-11ea-99a8-3f957097f4c9', 'd0b619ba-2ab1-11ea-ac32-43e650aafd4f'])
    assert result[0].method == '6b23435c-2ab1-11ea-99a8-3f957097f4c9' and result[0].result is False
    assert result[1].method == 'd0b619ba-2ab1-11ea-ac32-43e650aafd4f' and result[1].result is True
    assert result[2].method == '6b23435c-2ab1-11ea-99a8-3f957097f4c9' and result[2].result is True
    assert result[3].method == 'd0b619ba-2ab1-11ea-ac32-43e650aafd4f' and result[3].result is True


def test_exclusive():
    se = __prepare_instance()
    result = se.run_strategy(
        ['500002.SSZ', '300009.SESZ'],
        ['78ffae34-2ab1-11ea-88ff-634c407b44d3', 'd905cdea-2ab1-11ea-9e79-ff65d4808d88'])
    assert result[0].method == '78ffae34-2ab1-11ea-88ff-634c407b44d3' and result[0].result is True
    assert result[1].method == 'd905cdea-2ab1-11ea-9e79-ff65d4808d88' and result[1].result is True
    assert result[2].method == '78ffae34-2ab1-11ea-88ff-634c407b44d3' and result[2].result is True
    assert result[3].method == 'd905cdea-2ab1-11ea-9e79-ff65d4808d88' and result[3].result is False


def test_entry():
    test_analyzer_prob()
    test_score()
    test_inclusive()
    test_exclusive()


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

