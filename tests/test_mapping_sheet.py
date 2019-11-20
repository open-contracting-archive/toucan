from django.test import TestCase
from tests import read
from io import StringIO
from unittest.mock import patch


class MappingSheetTestCase(TestCase):
    url = '/mapping-sheet/'

    @patch('default.mapping_sheet.get_tags')
    def test_get(self, mock_get):
        mock_get.return_value = ("1__0__0", "1__0__1")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<option value="1__0__0">1.0.0</option>', content)
        self.assertIn('<option value="1__0__1">1.0.1</option>', content)

    def test_get_url(self):
        response = self.client.get(self.url, {
            'source': 'https://standard.open-contracting.org/schema/1__1__4/release-schema.json'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'), read('results/mapping-sheet.csv'))

    def test_post_select(self):
        response = self.client.post(self.url, {
            'type': 'select',
            'select_url': 'https://standard.open-contracting.org/schema/1__1__4/release-schema.json',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'), read('results/mapping-sheet.csv'))

    def test_post_url(self):
        response = self.client.post(self.url, {
            'type': 'url',
            'custom_url':
                'https://standard.open-contracting.org/schema/1__1__4/release-schema.json',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'),
                         read('results/mapping-sheet.csv'))

    def test_post_file(self):
        input_file = StringIO(read('schemas/ocds-ppp-1_0_0-release-schema.json'))
        input_file.name = 'test.json'

        response = self.client.post(self.url, {
            'type': 'file',
            'custom_file': input_file
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'),
                         read('results/ocds-ppp-1_0_0-mapping-sheet.csv'))

    @patch('default.mapping_sheet.get_tags')
    def test_get_extension(self, mock_get):
        mock_get.return_value = ("1__1__3", "1__1__4")

        response = self.client.get(self.url, {
            'version': '1__1__4',
            'extension': (
                ('https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/v1.1.4/' +
                 'extension.json'),
                ('https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4' +
                 '/extension.json')
            )
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'),
                         read('results/bids-location-mapping-sheet.csv'))

    @patch('default.mapping_sheet.get_tags')
    def test_post_extension(self, mock_get):
        mock_get.return_value = ("1__1__3", "1__1__4")

        response = self.client.post(self.url, {
            'type': 'extension',
            'version': '1__1__4',
            'extension_url_0':
                ('https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/v1.1.4/' +
                 'extension.json'),
            'extension_url_1':
                ('https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4' +
                 '/extension.json')
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'),
                         read('results/bids-location-mapping-sheet.csv'))

    def test_post_empty(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<ul class="errorlist"><li>', content)
        self.assertIn('Please choose an operation type', content)

    def test_post_error_messages(self):
        # "Select an URL" option, with no URL selected
        response = self.client.post(self.url, {
            'type': 'select'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<ul class="errorlist"><li>', content)
        self.assertIn('Please select an option', content)

        # "Provide an URL" option, with an empty input URL
        response = self.client.post(self.url, {
            'type': 'url'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<ul class="errorlist"><li>', content)
        self.assertIn('Please provide an URL', content)

        # "Upload a file" option, with no file provided
        response = self.client.post(self.url, {
            'type': 'file'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<ul class="errorlist"><li>', content)
        self.assertIn('Please provide a file', content)

        # "Extensions of Release Schema" option, with no URL provided
        response = self.client.post(self.url, {
            'type': 'extension'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<ul class="errorlist nonfield"><li>', content)
        self.assertIn('Provide at least one extension URL', content)
