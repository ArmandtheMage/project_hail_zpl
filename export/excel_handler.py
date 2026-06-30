import os

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Border, Side, Alignment
from openpyxl.styles import Font
from openpyxl.styles import PatternFill

class ExcelHandler:
    THIN_STYLE = Side(style="thin", color="FF0000")
    BORDER_STYLE = Border(left=THIN_STYLE, right=THIN_STYLE, top=THIN_STYLE, bottom=THIN_STYLE)
    BIGGER_BOLD_FONT = Font(size=14, bold=True)
    BIG_BOLD_FONT = Font(size=13, bold=True)
    BIGGER_FONT = Font(size=14)
    NORMAL_FONT = Font(size=12)
    ITALIC_FONT = Font(size=12, italic=True)
    ALIGNMENT_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ALIGNMENT_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ZPL_QUERY_FILL = ""
    DATE_QUERY_FILL = ""

    def __init__(self):
        self.workbook = Workbook()
        self.sheet = self.workbook.active # da modificare con get_sheet_by_name("Sheet1") o altri simili

    def fill_cell(self, cell_number:str, value: str, sheet: Worksheet | None = None,
                  font:Font = Font(), alignment:Alignment = Alignment(),
                  fill:PatternFill = PatternFill()):
        """
        Fill a cell with the specified value, font, alignment, and fill.
        """
        if sheet is None:
            sheet = self.sheet

        if not cell_number:
            raise ValueError("Cell reference cannot be empty.")
        cell = sheet[cell_number]
        cell.value = value
        if font:
            cell.font = font
        if alignment:
            cell.alignment = alignment
        if fill:
            cell.fill = fill


    def merge_and_fill(self, cell_range: str, value: str, sheet: Worksheet | None = None,
                       font:Font = Font(), alignment:Alignment = Alignment(),
                       fill:PatternFill = PatternFill()):
        if sheet is None:
            sheet = self.sheet

        sheet.merge_cells(cell_range)
        cell_coordinate = cell_range.split(':')[0]
        
        self.fill_cell(cell_coordinate, value, sheet, font, alignment, fill)


    def set_common_header(self, sheet: Worksheet | None = None):
        """
        Draw and fill the common header of a ZPL.
        """
        if sheet is None:
            sheet = self.sheet
        
        # Titolo principale
        self.merge_and_fill('C1:E1', "RAPPORTO DI PROVA\nTest Report", sheet,
                            self.BIGGER_FONT, self.ALIGNMENT_CENTER)

        # Data e pagina
        
        self.fill_cell('F1', "Data/Date", sheet, alignment=self.ALIGNMENT_CENTER)
        self.fill_cell('G1', "DATA ZPL", sheet, alignment=self.ALIGNMENT_CENTER)

        self.fill_cell('H1', "Pag/Page", sheet, alignment=self.ALIGNMENT_CENTER)
        self.fill_cell('I1', "5/6", sheet, alignment=self.ALIGNMENT_CENTER)
        
        self.sheet.row_dimensions[1].height = 36

        # Laboratorio
        self.fill_cell('B2', "Laboratorio Prove", sheet, font=self.BIGGER_FONT)
        self.fill_cell('B3', "Test Laboratory", sheet, font=self.ITALIC_FONT)

        # Numero ZPL
        self.merge_and_fill('C2:D3', "Numero/Number:", sheet, alignment=self.ALIGNMENT_LEFT)
        self.merge_and_fill('E2:I3', "NUMERO ZPL", sheet, font=Font(bold=True), alignment=self.ALIGNMENT_LEFT)

        # Info test
        self.merge_and_fill('B5:C5', "Esecutore del test / Test performer", sheet)
        self.merge_and_fill('D5:I5', "Inserire nome", sheet)

        
        self.merge_and_fill('B6:C6', "Oggetto di prova/Test Object", sheet)
        self.merge_and_fill('D6:I6', "inserire Gwc0de", sheet)

        self.merge_and_fill('B7:C7', "Nome prodotto", sheet)
        self.merge_and_fill('D7:I7', "inserire NomeProdotto", sheet)

        self.merge_and_fill('B8:C8', "Firmware Version", sheet)
        self.merge_and_fill('D8:I8', "inserre FW", sheet)

        # Conforme
        self.merge_and_fill('B9:C9', "Conforme/Conformance", sheet)
        self.merge_and_fill('D9:I9', "", sheet)

        # Nota
        self.merge_and_fill('D10:I10', "Inserire i dispositivi e i rispettivi fw dei prodotti utilizzati", sheet)

        # System info
        self.merge_and_fill('B10:C10', "System info & Configuration", sheet)


    def set_datasheet(self, sheet: Worksheet | None = None, start_row: int = 12, section: str = "", table_titles: list[str] =  [], data: list[tuple] = ()):
        """
        Draw and fill the specific data for that sheet.
        """
        if sheet is None:
            sheet = self.sheet

        # Implement datasheet drawing and filling logic here
        # set section title
        if section:
            #self.sheet[f"B{start_row}"] = section
            self.merge_and_fill(f"B{start_row}:I{start_row}", section, sheet, font=self.BIG_BOLD_FONT)
        
        # set titles
        for offset, title in enumerate(table_titles):
            self.sheet[f"{chr(66 + offset)}{start_row + 1}"] = title

        # set data
        for offset, row_data in enumerate(data):
            for col_offset, value in enumerate(row_data):
                if len(row_data) > len(table_titles):
                    raise ValueError(f"Data row has more columns than titles. Row data: {row_data}, Titles: {table_titles}")
                self.sheet[f"{chr(66 + col_offset)}{start_row + 2 + offset}"] = value

    def save(self, filename: str = "report_zpl.xlsx", parent_path: str = ""):
        if not parent_path:
            parent_path = os.getcwd()
        full_path = os.path.join(parent_path, filename)
        print(f"Saving Excel file to: {full_path}")
        self.workbook.save(full_path)


if __name__ == "__main__":
    excel_handler = ExcelHandler()
    excel_handler.set_common_header()
    excel_handler.set_datasheet(section = "ELENCO ISSUE E BUG / ISSUE AND BUG LIST", table_titles=[        
        "TYPE",
        "ID SEGNALAZIONE",
        "TITOLO",
        "ID TEST FAIL",
        "NOTE"], 
        data=[("Issue", "456789", "Titolo 1", "ID Test 1"),
              ("Bug", "123456", "Titolo 2")])
    excel_handler.save("test_report.xlsx")
