from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    import stock_analysis_system
    from Utiltity.common import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
except Exception as e:
    sys.path.append(root_path)

    import stock_analysis_system
    from Utiltity.common import *
    from Utiltity.time_utility import *
    from Analyzer.AnalyzerUtility import *
finally:
    pass


# ----------------------------------------------------------------------------------------------------------------------


def test_entry() -> bool:
    ret = True
    sas = stock_analysis_system.StockAnalysisSystem()

    data_hub = sas.get_data_hub_entry()
    se = sas.get_strategy_entry()

    stock_list = data_hub.get_data_utility().get_stock_list()
    stock_ids = [_id for _id, _name in stock_list]

    result = se.run_strategy(stock_ids, [
        # '7a2c2ce7-9060-4c1c-bca7-71ca12e92b09',
        # 'e639a8f1-f2f5-4d48-a348-ad12508b0dbb',
        # 'f39f14d6-b417-4a6e-bd2c-74824a154fc0',
        # '3b01999c-3837-11ea-b851-27d2aa2d4e7d',
        # '1fdee036-c7c1-4876-912a-8ce1d7dd978b',
        'b0e34011-c5bf-4ac3-b6a4-c15e5ea150a6',
    ])

    pass_securities = pick_up_pass_securities(result, 50)
    print(pass_securities)

    return ret


def main():
    test_entry()
    print('All Test Passed.')


# ----------------------------------------------------------------------------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass






















