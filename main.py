import sys
import time
import traceback
from PyQt5.QtWidgets import QApplication

import main_ui
import stock_analysis_system


def run_ui():
    app = QApplication(sys.argv)
    main_wnd = main_ui.MainWindow()
    main_wnd.show()
    app.exec_()


def update_local(update_list: [str], force: bool=False):
    sas = stock_analysis_system.StockAnalysisSystem()
    data_hub = sas.get_data_hub_entry()
    data_center = data_hub.get_data_center()
    data_utility = data_hub.get_data_utility()

    if 'Market.SecuritiesInfo' in update_list:
        print('Updating SecuritiesInfo...')
        data_center.update_local_data('Market.SecuritiesInfo', force=force)

    if 'Market.NamingHistory' in update_list:
        print('Updating Naming History...')
        data_center.update_local_data('Market.NamingHistory', force=force)

    if 'Market.TradeCalender' in update_list:
        print('Updating TradeCalender...')
        data_center.update_local_data('Market.TradeCalender', exchange='SSE', force=force)

    stock_list = data_utility.get_stock_list()

    start_total = time.time()
    print('Updating Finance Data for All A-SHARE Stock.')

    counter = 0
    for stock_identity, name in stock_list:
        start_single = time.time()
        print('Updating Finance Data for ' + stock_identity + ' [' + name + ']')
        if 'Finance.Audit' in update_list:
            data_center.update_local_data('Finance.Audit', stock_identity, force=force)
        if 'Finance.BalanceSheet' in update_list:
            data_center.update_local_data('Finance.BalanceSheet', stock_identity, force=force)
        if 'Finance.IncomeStatement' in update_list:
            data_center.update_local_data('Finance.IncomeStatement', stock_identity, force=force)
        if 'Finance.CashFlowStatement' in update_list:
            data_center.update_local_data('Finance.CashFlowStatement', stock_identity, force=force)

        counter += 1
        print('Done (%s / %s). Time Spending: %s s' % (counter, len(stock_list), time.time() - start_single))

        # For the sake of:
        # 抱歉，您每分钟最多访问该接口80次，权限的具体详情访问：https://tushare.pro/document/1?doc_id=108
        time.sleep(1)

    print('Update Finance Data for All A-SHARE Stock Done. Time Spending: ' + str(time.time() - start_total) + 's')


def update_special():
    sas = stock_analysis_system.StockAnalysisSystem()
    data_hub = sas.get_data_hub_entry()
    data_center = data_hub.get_data_center()
    data_utility = data_hub.get_data_utility()

    data_center.update_local_data('Finance.Audit', '000021.SZSE', force=True)


def run_strategy():
    pass


def run_console():
    # update_special()
    update_local([
        # 'Market.SecuritiesInfo',
        # 'Market.NamingHistory',
        # 'Market.TradeCalender',

        # 'Finance.Audit',
        # 'Finance.BalanceSheet',
        'Finance.IncomeStatement',
        # 'Finance.CashFlowStatement',
    ], True)
    # run_strategy()

    exit(0)


def main():
    sas = stock_analysis_system.StockAnalysisSystem()
    sas.check_initialize()

    run_console()
    # run_ui()


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
