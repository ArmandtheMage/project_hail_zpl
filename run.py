import sys
import os
import logging
from utils.ZPL_log import ZPLLogger
from gui.gui import GUI
from azure_project.azure_handler import AzureHandler
from export.excel_handler import ExcelHandler

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        # Running as built executable
        exe_name = os.path.basename(sys.executable).lower()
        if "debug" in exe_name or "--debug" in sys.argv:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
    else:
        # Running locally from source
        log_level = logging.DEBUG

    log = ZPLLogger("ZPLLogger", log_level=log_level)
    az = AzureHandler(logger=log)
    eh = ExcelHandler(logger=log)
    gui = GUI(logger=log, azure_handler=az, excel_handler=eh)
    gui.root.mainloop()