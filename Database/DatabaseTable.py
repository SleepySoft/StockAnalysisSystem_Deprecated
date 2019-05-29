import sys
import json
import traceback
from datetime import datetime

import config
import pymongo
from pymongo import MongoClient


def text2date(text: str) -> datetime:
    return datetime.strptime(text, '%Y-%m-%d')


def text2datetime(text: str) -> datetime:
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')


def date2text(time: datetime) -> str:
    return time.strftime('%Y-%m-%d')


def datetime2text(time: datetime) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S')


'''
Itkv = Identity, DateTime, Key, Value
This table is based on NoSQL (MongoDB)
It must contain an Identity and a Timestamp as unique index
Other Key-Value pairs are extendable
'''

class ItkvTable:
    def __init__(self, client: MongoClient, database: str, table: str):
        self.__client = client
        self.__database = database
        self.__table = table

    # Update a record, insert if not exists.
    # identity - The identity you want to update, must be str
    # time - The datetime you want to update, must be datetime
    # data - The data you want to update, must be dict
    # identity and time are also the conditions to find the entries
    def upsert(self, identity: str, time: datetime, data: dict) -> dict:
        collection = self.__get_collection()
        if collection is None:
            return False
        spec = self.__gen_find_spec(identity, time, time)
        document = {
            'Identity': identity,
            'DateTime': datetime2text(time),
            **data
        }
        return collection.update(spec, document, True)

    # Update a record, insert if not exists.
    # identity - The identity you want to delete, can be str or list
    # since - The datetime you want to delete from, must be datetime
    # until - The datetime you want to delete to, must be datetime
    # keys - The keys you want to remove, None to move the whole entry
    def delete(self, identity: str or list, since: datetime = None, until: datetime = None, keys: list = None):
        collection = self.__get_collection()
        if collection is None:
            return False
        spec = self.__gen_find_spec(identity, since, until)

        if keys is None:
            return collection.delete_many(spec)
        else:
            del_keys = {}
            for key in keys:
                del_keys[key] = 1
            return collection.update(spec, {'$unset': del_keys}, False, True)

    # Query records
    # identity - The identity you want to delete, can be str or list
    # since - The datetime you want to query from, must be datetime
    # until - The datetime you want to query to, must be datetime
    #         You can set since and until the same to do a accurate record
    # keys - The keys you want to query, None to query all
    def query(self, identity: str or list, since: datetime = None, until: datetime = None, keys: list = None) -> list:
        collection = self.__get_collection()
        if collection is None:
            return False
        spec = self.__gen_find_spec(identity, since, until)

        key_select = None
        if keys is not None:
            key_select = {}
            for key in keys:
                key_select[key] = 1

        return list(collection.find(spec, key_select))

    def __get_collection(self):
        if self.__client is None:
            return None
        db = self.__client[self.__database]
        if db is None:
            return None
        collection = db[self.__table]
        return collection

    def __gen_find_spec(self, identity: str or list, since: datetime = None, until: datetime = None) -> dict:
        if identity is None:
            spec = {}
        elif isinstance(identity, str):
            spec = {'Identity': identity}
        elif isinstance(identity, list):
            spec = {'Identity': {'$in': identity}}
        else:
            raise Exception('<identity> should be str or a list of str, or just None')

        time_limit = {}
        if since is not None:
            time_limit['$gte'] = datetime2text(since)
        if until is not None:
            time_limit['$lte'] = datetime2text(until)
        if len(time_limit) > 0:
            spec['DateTime'] = time_limit

        return spec


def main():
    client = MongoClient(config.DB_HOST, config.DB_PORT, serverSelectionTimeoutMS=5)
    table = ItkvTable(client, 'TestDB', 'TestDB')
    data1 = {
        'a': '1',
        'b': 2,
        'c': 3,
        'd': '2019-08-20 11:22:33',
    }
    data2 = {
        'c': '1',
        'd': 2,
        'e': 3,
        'f': 4,
    }
    table.upsert('000001', text2datetime('2018-08-18 11:22:33'), data1)
    table.upsert('000001', text2datetime('2019-09-29 22:33:44'), data2)

    result = table.query('000001')
    print(result)


# ----------------------------------------------------------------------------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


sys.excepthook = exception_hook


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass

