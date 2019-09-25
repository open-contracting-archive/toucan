import os
import tempfile

import requests
from django.test import TestCase, override_settings

from default.file import FilenameHandler
from default.flatten import flatten

EXAMPLE_RELEASE_URL = 'https://raw.githubusercontent.com/open-contracting/sample-data/master/fictional-example/1.1/ocds-213czf-000-00001-01-planning.json'  # noqa


class FlattenTest(TestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def setUp(self):
        # bring
        self.handler = FilenameHandler('test', '.json', id='release', folder='test')
        if not os.path.isdir(self.handler.get_folder()):
            os.mkdir(self.handler.get_folder())
        if not os.path.isfile(self.handler.get_full_path()):
            contents = requests.get(EXAMPLE_RELEASE_URL).text
            with open(self.handler.get_full_path(), 'w') as testfile:
                testfile.write(contents)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_flatten(self):
        flatten(self.handler)
        self.assertTrue(os.path.isfile(os.path.join(self.handler.get_folder(), 'flatten-release.xlsx')))
        self.assertTrue(os.path.isfile(os.path.join(self.handler.get_folder(), 'flatten-csv-release.zip')))
