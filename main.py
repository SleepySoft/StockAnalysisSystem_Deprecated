import sys
import traceback
from PyQt5.QtWidgets import QApplication

import main_ui
import stock_analysis_system


def main():
    sas = stock_analysis_system.StockAnalysisSystem()
    sas.check_initialize()

    app = QApplication(sys.argv)
    main_wnd = main_ui.MainWindow()
    main_wnd.show()
    app.exec_()


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
