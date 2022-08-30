"""Test the read_csv, read_excel, read_sqlite functions."""
import unittest

from tinytable.csv import read_csv_file
from tinytable.excel import read_excel_file
from tinytable.sqlite import read_sqlite_table


class TestReadCSV(unittest.TestCase):
    
    def test_excel_csv(self):
        data = read_csv_file('tests/data/people.csv')
        expected = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        self.assertDictEqual(data, expected)


class TestReadExcel(unittest.TestCase):

    def test_xlsx(self):
        data = read_excel_file('tests/data/people.xlsx', 'Sheet1')
        expected = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        self.assertDictEqual(data, expected)


class TestReadSql(unittest.TestCase):

    def test_sql(self):
        data = read_sqlite_table('tests/data/data.db', 'people')
        expected = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        self.assertDictEqual(data, expected)