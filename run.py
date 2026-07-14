from utils.ZPL_log import ZPLLogger
from gui.gui import GUI
from azure_project.azure_handler import AzureHandler
from export.excel_handler import ExcelHandler

if __name__ == "__main__":
    log = ZPLLogger("ZPLLogger")
    az = AzureHandler(logger=log)
    eh = ExcelHandler(logger=log)
    gui = GUI(logger=log, azure_handler=az, excel_handler=eh)
    gui.root.mainloop()