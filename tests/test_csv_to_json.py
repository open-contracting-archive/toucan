import json
import os.path
from io import BytesIO
from zipfile import ZipFile

from tests import ViewTestCase, ViewTests, path


class CsvToJsonTestCase(ViewTestCase, ViewTests):
    url = '/to-json/'
    files = [
        '1.1/spreadsheets/flattened.zip',
    ]

    def test_go_with_files(self):
        self.assertResults({}, {
            'result.json': 'results/unflattened_csv.json',
        }, mode='rb')
