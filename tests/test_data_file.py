import unittest
from datetime import date

from default.data_file import DataFile


class DataFileTestCase(unittest.TestCase):
    def test_repr_with_folder(self):
        data_file = DataFile('result', '.zip', id='identifier', folder='directory')

        assert repr(data_file) == 'directory/result-identifier.zip'


    def test_repr_without_folder(self):
        data_file = DataFile('result', '.zip', id='identifier')

        assert repr(data_file) == '{:%Y-%m-%d}/result-identifier.zip'.format(date.today())
