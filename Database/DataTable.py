# !usr/bin/env python
# -*- coding:utf-8 -*-

"""
@version:
author:Sleepy
@time: 2019/01/08
@file: Database.py
@function:
@modify:
"""

import os
try:
    from Database.UpdateTable import UpdateTable
except Exception as e:
    from os import sys, path
    root = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root)

    from Database.UpdateTable import UpdateTable
finally:
    pass


class DataTable:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
            cls._instance.__singleton_init()
        return cls._instance

    def __init__(self):
        # This function may be called multiple times.
        pass

    def __singleton_init(self):
        self.__update_table = UpdateTable()

    def get_update_table(self) -> UpdateTable:
        return self.__update_table

