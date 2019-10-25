from django.test import TestCase
from tests import read
from io import StringIO


class MappingSheetTestCase(TestCase):
    url = '/mapping-sheet/'

    def test_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_get_url(self):
        response = self.client.get(self.url, {
            'source': 'https://standard.open-contracting.org/1__1__4/en/release-schema.json'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'), read('results/mapping-sheet.csv'))

    def test_post_select(self):
        response = self.client.post(self.url, {
            'type': 'select',
            'select_url': 'https://standard.open-contracting.org/1__1__4/en/release-schema.json',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'), read('results/mapping-sheet.csv'))

    def test_post_url(self):
        response = self.client.post(self.url, {
            'type': 'url',
            'custom_url':
                'https://standard.open-contracting.org/profiles/ppp/1.0/en/_static/patched/release-schema.json',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'),
                         read('results/ocds-ppp-1_0_0-mapping-sheet.csv'))

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

    def test_get_extension(self):
        response = self.client.get(self.url, {
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

    def test_post_extension(self):
        response = self.client.post(self.url, {
            'type': 'extension',
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
