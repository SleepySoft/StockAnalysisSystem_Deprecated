from Database.DatabaseRW import DatabaseRW
from datetime import datetime


# Identity, Time, Key, Value

class ItkvTable:

    def __init__(self, table_name: str, dbrw: DatabaseRW):
        self.__dbrw = dbrw
        self.__table_name = table_name

    def init(self) -> bool:
        if not self.__dbrw.TableExists(self.__table_name):
            self.__dbrw.CreateTable([
                ['Identity',    'varchar(255)'],
                ['Time',        'varchar(DATETIME)'],
                ['Key',         'varchar(255)'],
                ['Value',       'varchar(1024)'],
            ])

    def GetColumns(self) -> list:
        return self.__dbrw.GetTableColumns(self.__table_name)

    def QueryData(self, identity: str, keys: list, time_from: datetime, time_to: datetime) -> list:
        sql = ("SELECT * FROM %s WHERE Identity = '%s' AND Key In (%s) AND Time >= '%s' AND Time <= %s;" %
               self.__table_name, identity, ', '.join(keys), time_from)







