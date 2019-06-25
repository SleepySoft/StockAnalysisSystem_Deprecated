import traceback

import numpy as np
import pandas as pd

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))


def check_date_continuity(df: pd.DataFrame, field: str) -> tuple:
    """
    Check the continuity of a date format column in a DataFrame
    :param df: DataFrame for check
    :param field: The datetime filed you want to check
    :return: tuple (continuity: bool, start date: datetime, end date: datetime)
    """
    date_serial = pd.Series(data=1, index=df[field])
    date_serial.sort_index()
    min_date = min(date_serial.index)
    max_date = max(date_serial.index)
    date_serial.reindex(index=pd.date_range(min_date, max_date), fill_value=0)
    continuity = 0 not in date_serial.data
    return continuity, min_date, max_date


def concat_dataframe_by_index(dfs: [pd.DataFrame]) -> pd.DataFrame:
    """
    Concat DataFrame by row. Remove the rows in the result which has duplicated index.
    :param dfs: The list of DataFrame you want to concat.
    :return: The result DataFrame
    """
    df = pd.concat(dfs)
    df = df.loc[~df.index.duplicated(keep='first')]
    return df


def clip_dataframe(df: pd.DataFrame, indexes: [int], columns: [str]):
    """
    Clip DataFrame by specified indexes and columns. If data not exists, nan will be filled.
    :param df: The DataFrame you want to clip
    :param indexes: The indexes you pick
    :param columns: The columns you pick
    :return: The result DataFrame
    """
    df_sub = pd.DataFrame()
    for c in columns:
        if c not in df.columns:
            serial = np.empty(df.shape[0])
            serial.fill(np.nan)
        else:
            serial = df[c]
        df_sub.insert(len(df_sub.columns), c, serial)
    return df_sub.loc[indexes]


# ----------------------------------------------------------------


def MergeDataFrameOnIndex(df_l: pd.DataFrame, df_r: pd.DataFrame):
    if df_l is None:
        return df_r
    if df_r is None:
        return df_l
    return pd.merge(df_l, df_r, left_index=True, right_index=True, how='outer')


def MergeDataFrameOnColumn(df_l: pd.DataFrame, df_r: pd.DataFrame, on_col: str):
    if df_l is None or on_col not in df_l.columns:
        return df_r
    if df_r is None or on_col not in df_r.columns:
        return df_l
    return pd.merge(df_l, df_r, on=on_col, how='outer')


# return (copied, uncopied)
def DataFrameColumnCopy(df_from: pd.DataFrame, df_to: pd.DataFrame, columns: [str]) -> (int, int):
    copied = uncopied = 0
    for c in columns:
        if c not in df_from.columns.tolist():
            uncopied += 1
            continue
        col = df_from[c]
        if c not in df_to.columns.tolist():
            df_to.insert(len(df_to.columns), c, col.copy())
        else:
            df_to[c] = col.copy()
        copied += 1
    return copied, uncopied


# ----------------------------------------------------- Test Code ------------------------------------------------------


def test_check_date_continuity():
    df = pd.DataFrame.from_csv(root_path + '/TestData/trade_calender.csv')
    continuity, min_date, max_date = check_date_continuity(df, 'TradeDate')
    print('continuity = ' + str(continuity))
    print('min_date = ' + str(min_date))
    print('max_date = ' + str(max_date))


def test_concat_dataframe_by_index():
    df1 = pd.DataFrame(data={
        'a': ['1A', '2A', '3A'],
        'b': ['1B', '2B', '3B'],
        'c': ['1C', '2C', '3C'],
    }, index=['2001-01-01', '2001-01-02', '2001-01-03'])
    df2 = pd.DataFrame(data={
        'a': ['3Ax', '4A', '5A'],
        'b': ['3Bx', '4B', '5B'],
        'c': ['3Cx', '4C', '5C'],
    }, index=['2001-01-03', '2001-01-04', '2001-01-05'])
    print(df1)
    print('---------------------------------------------------------------')
    print(df2)
    print('---------------------------------------------------------------')

    df = concat_dataframe_by_index([df1, df2])
    print(df)


def test_entry():
    test_check_date_continuity()
    test_dataframe_extend()


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











