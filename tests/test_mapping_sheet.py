import re
from unittest.mock import patch

from django.test import TestCase

from tests import path, read


class MappingSheetTestCase(TestCase):
    url = '/mapping-sheet/'

    def assertSuccess(self, method, expected, data):
        response = getattr(self.client, method)(self.url, data)

        if not (method == 'get' and ('source' in data.keys() or 'extension' in data.keys())):
            self.assertEqual(response.status_code, 200)
            content = response.content.decode('utf-8')
            self.assertIn('<div class="response-success alert alert-info">', content)

            response_url = re.search(r'/result/\d{4}\-\d{2}\-\d{2}/[0-9a-fA-F\-]{36}/csv/', content).group(0)

            response = self.client.get(response_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="result.csv"')
        self.assertEqual(response.getvalue().decode('utf-8').replace('\r\n', '\n'), read(expected))

    def assertError(self, data, message, nonfield=None):
        response = self.client.post(self.url, data)
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        if nonfield:
            self.assertIn('<ul class="errorlist nonfield"><li>', content)
        else:
            self.assertIn('<ul class="errorlist"><li>', content)
        self.assertIn(message, content)

    @patch('default.forms._get_tags')
    def test_get(self, mocked):
        mocked.return_value = ('1__0__0', '1__0__1')

        response = self.client.get(self.url)
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.assertIn('<option value="1__0__0">1.0.0</option>', content)
        self.assertIn('<option value="1__0__1">1.0.1</option>', content)

    def test_get_url(self):
        self.assertSuccess('get', 'results/mapping-sheet.csv', {
            'source': 'https://standard.open-contracting.org/schema/1__1__4/release-schema.json'
        })

    def test_post_select(self):
        self.assertSuccess('post', 'results/mapping-sheet.csv', {
            'type': 'select',
            'select_url': 'https://standard.open-contracting.org/schema/1__1__4/release-schema.json',
        })

    def test_post_url(self):
        self.assertSuccess('post', 'results/mapping-sheet.csv', {
            'type': 'url',
            'custom_url': 'https://standard.open-contracting.org/schema/1__1__4/release-schema.json',
        })

    def test_post_file(self):
        with open(path('schemas/ocds-ppp-1_0_0-release-schema.json')) as f:
            self.assertSuccess('post', 'results/ocds-ppp-1_0_0-mapping-sheet.csv', {
                'type': 'file',
                'custom_file': f,
            })

    @patch('default.forms._get_tags')
    def test_get_extension(self, mocked):
        mocked.return_value = ('1__1__3', '1__1__4')

        self.assertSuccess('get', 'results/bids-location-mapping-sheet.csv', {
            'version': '1__1__4',
            'extension': [
                'https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/v1.1.4/extension.json',  # noqa
                'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4/extension.json',  # noqa
            ]
        })

    @patch('default.forms._get_tags')
    def test_post_extension(self, mocked):
        mocked.return_value = ('1__1__3', '1__1__4')

        self.assertSuccess('post', 'results/bids-location-mapping-sheet.csv', {
            'type': 'extension',
            'version': '1__1__4',
            'extension_url_0': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/v1.1.4/extension.json',  # noqa
            'extension_url_1': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4/extension.json',  # noqa
        })

    def test_post_empty(self):
        self.assertError({}, 'Please choose an operation type')

    def test_post_error_select(self):
        self.assertError({'type': 'select'}, 'Please select an option')

    def test_post_error_url(self):
        self.assertError({'type': 'url'}, 'Please provide a URL')

    def test_post_error_file(self):
        self.assertError({'type': 'file'}, 'Please provide a file')

    def test_post_error_extension(self):
        self.assertError({'type': 'extension'}, 'Provide at least one extension URL', nonfield=True)
