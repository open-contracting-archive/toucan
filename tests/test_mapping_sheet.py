from django.test import TestCase


class MappingSheetTestCase(TestCase):
    url = '/mapping-sheet/'

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_post_without_version(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

        content = response.content.decode('utf-8')
        self.assertIn('<div class="alert alert-warning">', content)
        self.assertIn('Invalid option! Please verify and try again', content)

    def test_post(self):
        response = self.client.post(self.url, {'version': '1.1-Release'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="mapping-sheet.csv"')
