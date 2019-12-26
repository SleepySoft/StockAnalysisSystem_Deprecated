import logging

import numpy as np
import pandas as pd
from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import Utiltity.common as common
    from Database.DatabaseEntry import DatabaseEntry
    from Utiltity.plugin_manager import PluginManager
    from DataHub.UniversalDataCenter import ParameterChecker
    from DataHub.UniversalDataCenter import UniversalDataTable
    from DataHub.UniversalDataCenter import UniversalDataCenter
except Exception as e:
    sys.path.append(root_path)

    import Utiltity.common as common
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
    df.to_csv(csv_file + 'id')


class DataUtility:
    def __init__(self, data_center: UniversalDataCenter):
        self.__data_center = data_center

    def get_stock_list(self) -> [(str, str)]:
        result = self.__data_center.query('Market.SecuritiesInfo', fields=['stock_identity', 'name'])
        return [(line.get('stock_identity', ''), line.get('name', '')) for line in result]

    def names_to_stock_identity(self, names: [str]):
        if not isinstance(names, list):
            names = [str(names)]
        stock_list = self.get_stock_list()
        name_id_table = {stock_name: stock_id for stock_id, stock_name in stock_list}

        ids = []
        for name in names:
            name = name_id_table.get(name, name)
            identity = common.normalize_stock_identity(name)
            ids.append(identity if identity != '' else name)
        return ids






















