import xlwings as xw
from src.common.ExcelReaderProvider import ExcelReaderProvider


class XlwingProvider(ExcelReaderProvider):

    # Connect to an existing Excel instance or start a new one
    _app = xw.App(visible=True)

    def get_workbook(self, path: str):
        # Open an existing workbook
        wb = self._app.books.open(path)
        return wb

    def get_worksheet(self, workbook, sheet_name:str):
        ws = workbook.sheets[sheet_name]
        return ws

    def change_value_at(self, worksheet, row, column, value):
        worksheet.range((row, column)).value = value
        return True

    def get_value_at(self, worksheet, row, column):
        return worksheet.range((row, column)).value

    def save(self, workbook):
        workbook.save()

    def close(self, workbook):
        workbook.close()
        self._app.quit()
