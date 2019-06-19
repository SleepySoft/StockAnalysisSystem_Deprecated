import sys
import traceback
import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database.Database import Database
    from Database import UpdateTable
    from Database.DataTable import DataTable
    from Utiltity.plugin_manager import PluginManager
except Exception as e:
    sys.path.append(root_path)

    from Utiltity.df_utility import *
    from Utiltity.time_utility import *
    from Database.Database import Database
    from Database import UpdateTable
    from Database.DataTable import DataTable
    from Utiltity.plugin_manager import PluginManager
finally:
    pass


class DataUtility:
    def __init__(self, plugin: PluginManager, update: UpdateTable):
        self.__plugin = plugin
        self.__update = update

    def query_data(self, **kwargs) -> pd.DataFrame:
        self.check_update()
        pass

    def check_update(self, since: datetime, until: datetime):
        if self.need_update():
            self.execute_update()

    def need_update(self) -> bool:
        update_tag = self.get_data_update_tag()
        self.__update.

    def execute_update(self):
        pass

    def get_data_update_tag(self, **kwargs) -> [str, str, str]:
        return ['', '', '']

    def reference_data_range(self) -> [datetime, datetime]:
        return [text2date('1900-01-01'), yesterday()]

    def reference_latest_update(self) -> datetime:
        return yesterday()

    def load_data(self, **kwargs):
        pass

    def fetch_data(self, **kwargs):
        pass















