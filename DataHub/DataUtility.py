import logging

import numpy as np
import pandas as pd
from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common
    from Utiltity.time_utility import *
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common
    from Utiltity.time_utility import *
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
finally:
    logger = logging.getLogger('')


def csv_name_column_to_identity(csv_file: str, column: str) -> bool:
    df = pd.read_csv(csv_file, index_col=None)
    if column not in list(df.columns):
        return False
    from stock_analysis_system import StockAnalysisSystem
    data_utility = StockAnalysisSystem().get_data_hub_entry().get_data_utility()
    name_column = df[column].values.tolist()
    id_column = data_utility.names_to_stock_identity(name_column)
    df[column] = np.array(id_column)
    df.to_csv(csv_file + '_parsed.csv')


class DataUtility:
    def __init__(self, data_center: UniversalDataCenter):
        self.__data_center = data_center

        self.__stock_id_using_name_table = {}
        self.__stock_history_name_id_table = {}

    def refresh_securities_cache(self):
        securities_info = self.__data_center.query('Market.SecuritiesInfo',
                                                   fields=['stock_identity', 'name'])
        if securities_info is not None:
            self.__stock_id_using_name_table = {line.get('stock_identity'): line.get('name')
                                                for line in securities_info}

        securities_used_name = self.__data_center.query('Market.NamingHistory',
                                                        fields=['stock_identity', 'name', 'naming_date'])
        if securities_used_name is not None:
            self.__stock_history_name_id_table = {
                # Convert to lower case and remove * mark for easy indexing.
                line.get('name', '').lower().replace('*', ''): (line.get('stock_identity'),
                                                                line.get('naming_date'))
                for line in securities_used_name}
            
            # Also add current name into history naming list
            if securities_info is not None:
                for key, value in self.__stock_id_using_name_table.items():
                    trimed_name = value.lower().replace('*', '')
                    if trimed_name not in self.__stock_history_name_id_table.keys():
                        self.__stock_history_name_id_table[trimed_name] = (key, today())

    def get_stock_list(self) -> [(str, str)]:
        if len(self.__stock_id_using_name_table) == 0:
            self.refresh_securities_cache()
        return [(_id, _name) for _id, _name in self.__stock_id_using_name_table.items()]
        # result = self.__data_center.query('Market.SecuritiesInfo', fields=['stock_identity', 'name'])
        # return [(line.get('stock_identity', ''), line.get('name', '')) for line in result]

    def names_to_stock_identity(self, names: [str]) -> [str]:
        if len(self.__stock_id_using_name_table) == 0:
            self.refresh_securities_cache()
        if not isinstance(names, list):
            names = [str(names)]
        # The result is a tuple like (stock_identity, naming_date)
        # We'll keep the original name if there's no match record.
        # Too simple: [self.__stock_history_name_id_table.get(name, (name, ''))[0] for name in names]

        ids = []
        for name in names:
            _id = self.__stock_history_name_id_table.get(name.lower(), ('', ''))[0]
            if _id != '':
                ids.append(_id)
            else:
                # For debug
                ids.append(name)
        return ids

        # stock_list = self.get_stock_list()
        # name_id_table = {stock_name: stock_id for stock_id, stock_name in stock_list}
        #
        # ids = []
        # for name in names:
        #     name = name_id_table.get(name, name)
        #     identity = common.normalize_stock_identity(name)
        #     ids.append(identity if identity != '' else name)
        # return ids






















