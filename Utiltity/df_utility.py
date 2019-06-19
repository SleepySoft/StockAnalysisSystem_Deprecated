import traceback

import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))


def check_date_continuity(df: pd.DataFrame, field: str) -> ():
    """
    :param df: DataFrame for check
    :param field: The datetime filed
    :return: tuple (continuity: bool, start date: datetime, end date: datetime)
    """

    date_serial = pd.Series(data=1, index=df[field])
    date_serial.sort_index()
    min_date = min(date_serial.index)
    max_date = max(date_serial.index)
    date_serial.reindex(index=pd.date_range(min_date, max_date), fill_value=0)
    continuity = 0 not in date_serial.data
    return continuity, min_date, max_date


# ----------------------------------------------------- Test Code ------------------------------------------------------


def test_check_date_continuity():
    df = pd.DataFrame.from_csv(root_path + '/TestData/trade_calender.csv')
    continuity, min_date, max_date = check_date_continuity(df, 'TradeDate')
    print('continuity = ' + str(continuity))
    print('min_date = ' + str(min_date))
    print('max_date = ' + str(max_date))


def test_entry():
    test_check_date_continuity()


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











