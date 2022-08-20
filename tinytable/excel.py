from typing import Optional, Union

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from openpyxl.chartsheet.chartsheet import Chartsheet
from tinytim.functional.utils import combine_names_rows


Sheet = Union[Worksheet, ReadOnlyWorksheet, Chartsheet]
WorkSheet = Union[Worksheet, ReadOnlyWorksheet]


class WorkBook:
    def __init__(self, path: str) -> None:
        self.path = path

    def __enter__(self):
        self.wb = openpyxl.load_workbook(self.path)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.wb.close()

    @property
    def active(self) -> Worksheet:
        return self.wb.active

    def __getitem__(self, key: str) -> Sheet:
        return self.wb[key]


def read_excel_file(path: str, sheet_name: Optional[str] = None) -> dict:
    """
    Reads a table object from given excel file path.
    """
    column_names = []
    rows = []
    first = True
    with WorkBook(path) as wb:
        ws = wb.active if sheet_name is None else wb[sheet_name]
        if isinstance(ws, Chartsheet):
            raise TypeError('Chartsheet has no values to read into table.')
        for row in ws.values:
            if first:
                column_names = row
                first = False
            else:
                rows.append(row)

    return combine_names_rows(column_names, rows)