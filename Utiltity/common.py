from datetime import time, datetime

import requests
import traceback
import numpy as np
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup


# -----------------------------------------------------------------------------------------------------

def nop(*args):
    pass


def slog(text: str):
    print(text)


def log_dbg(text: str):
    print(text)


def log_info(text: str):
    slog(text)


def log_error(text: str):
    slog(text)


# -------------------------------------------- Web related --------------------------------------------

def Download(url: str) -> bytes:
    try:
        r = requests.get(url)
        return r.content
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        return None
    finally:
        pass
    return None


def DownloadText(url: str, decode='gb2312') -> str:
    c = Download(url)
    if c is not None:
        return c.decode(decode)
    return ''


def DownloadCsvAsDF(url, decode='gb2312') -> pd.DataFrame:
    content = Download(url)
    return pd.read_csv(BytesIO(content), header=None, encoding=decode)


def GetWebAsSoap(url, decode='gb2312'):
    content = DownloadText(url, decode)
    return BeautifulSoup(content, "html.parser")


# -------------------------------------------- XML parse --------------------------------------------

# chain: [(tag, {properties}), ...]
def ChainParse(root, chain, find_list: []):
    if len(chain) == 0:
        return
    tag, properties = chain[0]
    childs = root.find_all(tag, properties)  # , recursive=(len(properties) > 0)
    if len(chain) == 1:
        find_list.extend(childs)
    else:
        for child in childs:
            ChainParse(child, chain[1:], find_list)


# -------------------------------------------- Type parse --------------------------------------------

def str2int_safe(text: str, default=0, base=10) -> float:
    try:
        return int(text, base)
    except Exception as e:
        return default
    finally:
        pass


def str2float_safe(text: str, default=0.0) -> float:
    try:
        return float(text)
    except Exception as e:
        return default
    finally:
        pass


def str_is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except Exception as e:
        return False
    finally:
        pass


def do_limitation(number: int, minimal: int, maximum: int) -> int:
    num = max(number, min(minimal, maximum))
    num = min(num, max(minimal, maximum))
    return num


def correct_start_end(start: int, end: int) -> tuple:
    _start = min(start, end)
    _end = max(start, end)
    return _start, _end


def correct_start_end(start: int, end: int, start_limit: int, end_limit: int) -> tuple:
    _start = min(start, end)
    _end = max(start, end)
    _start = do_limitation(_start, start_limit, end_limit)
    _end = do_limitation(_end, start_limit, end_limit)
    return _start, _end


# -------------------------------------------- DataFrame operation --------------------------------------------

def ClipDataFrame(df: pd.DataFrame, index: [int], columns: [str]):
    df_sub = pd.DataFrame()
    for c in columns:
        if c not in df.columns:
            serial = np.empty(df.shape[0])
            serial.fill(np.nan)
        else:
            serial = df[c]
        df_sub.insert(len(df_sub.columns), c, serial)
    return df_sub.loc[index]


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


# -------------------------------------------- Date/Time --------------------------------------------


# Parse ####-##-## format date
# Return (year, month, day)
def str_to_date(text: str) -> tuple:
    splited = text.split('-')
    while len(splited) < 3:
        splited.append('0')
    return tuple([str2int_safe(s) for s in splited])


# ms in float format
def TickCount() -> float:
    return time.clock()


def Date() -> tuple:
    dt = datetime.now()
    return dt.year, dt.month, dt.day


def Time() -> tuple:
    dt = datetime.now()
    return dt.hour, dt.minute, dt.second


def DateTimeString() -> str:
    return datetime.now().isoformat()


# -------------------------------------------- Sort algorithm --------------------------------------------

def topological_sort(source):
    """perform topo sort on elements.

    :arg source: list of ``(name, [list of dependancies])`` pairs
    :returns: list of names, with dependancies listed first
    """
    pending = [(name, set(deps)) for name, deps in source] # copy deps so we can modify set in-place
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted) # remove deps we emitted last pass
            if deps: # still has deps? recheck during next pass
                next_pending.append(entry)
            else: # no more deps? time to emit
                yield name
                emitted.append(name) # <-- not required, but helps preserve original ordering
                next_emitted.append(name) # remember what we emitted for difference_update() in next pass
        if not next_emitted: # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending,))
        pending = next_pending
        emitted = next_emitted


# -------------------------------------------- set --------------------------------------------


def set_missing(set_test, set_base) -> list:
    set1, set2 = set(set_test), set(set_base)
    return [i for i in set1 if i not in set2]


# -------------------------------------------- Stock related --------------------------------------------

# ss: Shanghai
# sz: Shenzhen
def GetStockMarket(stock_code: str) -> str:
    if len(stock_code) != 6:
        return ''
    if stock_code[0:2] == '00' or stock_code[0:3] == '200' or stock_code[0:3] == '300':
        return 'sz'
    if stock_code[0:2] == '60' or stock_code[0:3] == '900':
        return 'ss'
    return ''
