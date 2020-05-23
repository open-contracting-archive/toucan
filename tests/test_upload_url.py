import json
from datetime import date
from io import BytesIO
from unittest.mock import Mock, patch
from zipfile import ZipFile

from django.test import TestCase
from requests.exceptions import ConnectionError

from tests import read


class UploadUrlTestCase(TestCase):
    url = '/combine-packages/'
    files_urls = {
        'input_url_0': 'https://raw.githubusercontent.com/open-contracting/toucan/'
                       'master/tests/fixtures/1.1/release-packages/0001-tender.json',
        'input_url_1': 'https://raw.githubusercontent.com/open-contracting/toucan/'
                       'master/tests/fixtures/1.1/release-packages/0001-award.json',
        'input_url_2': 'https://raw.githubusercontent.com/open-contracting/toucan/'
                       'master/tests/fixtures/1.1/release-packages/0002-tender.json',
        'input_url_3': 'https://raw.githubusercontent.com/open-contracting/toucan/'
                       'master/tests/fixtures/1.1/release-packages/0003-array-packages.json'
    }
    results = {'result.json': 'results/combine_release_packages.json'}

    def test_upload_urls(self):
        response = self.client.post('/upload-url/', self.files_urls)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        response = self.client.get(self.url + 'go/?packageType=release')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        keys = ['url', 'size']
        content = json.loads(response.content.decode('utf-8'))
        for key in keys:
            self.assertIn(key, content.keys())
        self.assertEqual(len(content), len(keys))

        self.assertIsInstance(content['size'], int)
        self.assertRegex(content['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/$')

        response = self.client.get(content['url'])
        zipfile = ZipFile(BytesIO(response.getvalue()))

        for pattern, part in self.results.items():
            self.assertEqual(zipfile.read(pattern).decode('utf-8').replace('\r\n', '\n'), read(part))

    def test_bad_urls(self):
        bad_files_urls = {
            'input_url_0': 'https://raw.githubusercontent.com/open-contracting/toucan/'
                           'master/tests/fixtures/1.1/release-packages/0001-tender.json',
            'input_url_1': 'badurl'
        }
        response = self.client.post('/upload-url/', bad_files_urls)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'[{"id": "input_url_1", "message": "Enter a valid URL."}]')

    @patch('default.views.requests')
    def test_fail_connection(self, mock_requests):
        mock_requests.get = Mock(side_effect=ConnectionError())
        response = self.client.post('/upload-url/', {'input_url_0': self.files_urls['input_url_0']})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b'[{"id": "input_url_0", "message": "There was an error when trying to access this URL."}]')

    @patch('default.views.os')
    def test_folder_creation(self, mock_os):
        mock_os.stat = Mock(side_effect=FileNotFoundError())
        mock_os.mkdir = Mock(side_effect=FileNotFoundError())
        with self.assertRaises(FileNotFoundError):
            self.client.post('/upload-url/', {'input_url_0': self.files_urls['input_url_0']})
