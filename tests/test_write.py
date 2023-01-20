"""Test the data_to_csv, data_to_excel, data_to_sqlite functions."""
import unittest
import os
import filecmp

from tinytable.csv import data_to_csv_file
from tinytable.excel import data_to_excel_file
from tinytable.sqlite import data_to_sqlite_table


CSV_TEXT = """id,name,age,gender
1,Olivia,4,f
2,Noah,5,m
3,Emma,8,f
4,Liam,3,m
5,Amelia,24,f
6,Oliver,56,m
7,Ava,12,f
8,Elijah,68,m
9,Sophia,21,f
10,Mateo,90,m"""


def delete_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


class TestReadCSV(unittest.TestCase):
    
    def test_excel_csv(self):
        path = 'tests/data/new_people.csv'
        delete_file(path)
        data = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        data_to_csv_file(data, path)
        expected = CSV_TEXT
        with open(path, 'r') as f:
            str_data = f.read()
        self.assertEqual(str_data, expected)


class TestReadExcel(unittest.TestCase):

    def test_xlsx(self):
        path = 'tests/data/new_people.xlsx'
        copy_path = 'tests/data/new_people_copy.xlsx'
        delete_file(path)
        data = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        data_to_excel_file(data, path, replace_workbook=True)
        self.assertTrue(filecmp.cmp(path, copy_path))


class TestReadSql(unittest.TestCase):

    def test_sql(self):
        data = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        data_to_sqlite_table(data, 'data.db', 'people', replace_table=True)
        expected = {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'name': ['Olivia', 'Noah', 'Emma', 'Liam', 'Amelia', 'Oliver',
                             'Ava', 'Elijah', 'Sophia', 'Mateo'],
                    'age': [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
                    'gender': ['f', 'm', 'f', 'm', 'f', 'm', 'f', 'm', 'f', 'm']}
        self.assertDictEqual(data, expected)