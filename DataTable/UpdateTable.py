#!usr/bin/env python
#-*- coding:utf-8 _*-
import sys
import traceback
from datetime import datetime
from Database.Database import Database


class UpdateTable:
    TABLE = 'UpdateTable'
    FIELD = ['Serial', 'L1Tag', 'L2Tag', 'L3Tag', 'LastUpdate']

    def __init__(self):
        pass

    def renew_update_time(self, tag1: str, tag2: str, tag3: str):

        """
        https://codeday.me/bug/20170801/47985.html

        -- Try to update any existing row
            UPDATE players
            SET user_name='steven', age=32
            WHERE user_name='steven';

        -- If no update happened (i.e. the row didn't exist) then insert one
            INSERT INTO players (user_name, age)
            SELECT 'steven', 32
            WHERE (Select Changes() = 0);
        """

        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')

        sql_update = ("UPDATE %s SET LastUpdate = '%s' WHERE L1Tag='%s' AND L2Tag='%s' AND L3Tag='%s';" %
                      (date_str, tag1, tag2, tag3))

        sql_insert = ("INSERT INTO %s (L1Tag, L2Tag, L3Tag, LastUpdate) " + \
                      "SELECT '%s', '%s', '%s', '%s' WHERE (Select Changes() = 0);" %
                      (tag1, tag2, tag3, date_str))

        Database().GetUtilityDB().QuickExecuteDML(sql_update)
        Database().GetUtilityDB().QuickExecuteDML(sql_insert)

    def delete_update_record(self, tag1: str, tag2: str, tag3: str):
        pass

    def get_latest_update_time(self, tag1: str, tag2: str, tag3: str) -> datetime:
        result = Database().GetUtilityDB().ListFromDB(
            UpdateTable.TABLE, UpdateTable.FIELD, "L1Tag = '%s' AND L2Tag = '%s' AND L3Tag = '%s'" % (tag1, tag2, tag3))
        return None if len(result) > 0 else result


# ----------------------------------------------------- Test Code ------------------------------------------------------


def test_basic_feature():
    ut = UpdateTable()
    ut.renew_update_time('Finance Data', 'Annual', '000001')



# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():

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










