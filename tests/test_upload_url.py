import json
from datetime import date
from unittest.mock import Mock, patch

from django.test import TestCase


class UploadUrlTestCase(TestCase):
    url = '/combine-packages/'
    files_urls = [
        'https://raw.githubusercontent.com/open-contracting/toucan/master/tests/fixtures/1.1/release-packages/'
        '0001-award.json',
        'https://raw.githubusercontent.com/open-contracting/toucan/master/tests/fixtures/1.1/release-packages/'
        '0003-array-packages.json',
        'https://raw.githubusercontent.com/open-contracting/toucan/master/tests/fixtures/1.1/release-packages/'
        '0002-tender.json',
        'https://raw.githubusercontent.com/open-contracting/toucan/master/tests/fixtures/1.1/release-packages/'
        '0001-tender.json'
    ]

    def test_upload_urls(self):
        response = self.client.post('/upload-url/', {'input_url': self.files_urls})
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

    def test_fail_upload_urls(self):
        response = self.client.post('/upload-url/', {'input_url': 'badurl'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    @patch('default.views.os')
    def test_folder_creation(self, mock_os):
        mock_os.stat = Mock(side_effect=FileNotFoundError())
        mock_os.mkdir = Mock(side_effect=FileNotFoundError())
        with self.assertRaises(FileNotFoundError):
            self.client.post('/upload-url/', {'input_url': self.files_urls[0]})
