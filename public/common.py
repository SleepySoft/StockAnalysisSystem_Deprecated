import requests
import traceback
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup


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


def NamingStandardization(name: str) -> str:
    return name.strip().replace(' ', '_').lower()


# ss: Shanghai
# sz: Shengzhen
def GetStockMarket(stock_code: str) -> str:
    if len(stock_code) != 6:
        return ''
    if stock_code[0:2] == '00' or stock_code[0:3] == '200' or stock_code[0:3] == '300':
        return 'sz'
    if stock_code[0:2] == '60' or stock_code[0:3] == '900':
        return 'ss'
    return ''

def MergeDataFrameOn(df_l:pd.DataFrame, df_r:pd.DataFrame, on_col: str):
    if df_l is None or on_col not in df_l.columns:
        return df_r
    if df_r is None or on_col not in df_r.columns:
        return df_l
    return pd.merge(df_l, df_r, on=on_col)

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

