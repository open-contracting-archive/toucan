from django.test import TestCase

from tests import read


class MappingSheetTestCase(TestCase):
    url = '/mapping-sheet/'

    def test_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_post_with_version(self):
        response = self.client.post(self.url, {
            'url': 'https://standard.open-contracting.org/latest/en/release-schema.json',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
        self.assertEqual(response.content.decode('utf-8').replace('\r\n', '\n'), read('results/mapping-sheet.csv'))

    def test_post_without_version(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')

        self.assertIn('<div class="alert alert-warning">', content)
        self.assertIn('Invalid option! Please verify and try again', content)
