import json
import os.path

from tests import ViewTestCase, ViewTests


def path(filename):
    return os.path.join('tests', 'fixtures', filename)


class XlsxToJsonTestCase(ViewTestCase, ViewTests):
    url = '/to-json/'
    files = [
        '1.1/spreadsheets/flattened.xlsx',
    ]

    def test_go_with_files(self):

        for file in self.files:
            with open(path(file), 'rb') as f:
                self.client.post('/upload/', {'file': f})

        response = self.client.get(self.url + 'go/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(content), 2)
        self.assertIsInstance(content['size'], int)

        response = self.client.get(content['url'])
        result = response.getvalue()

        with open(path('results/unflattened_xlsx.json'), 'rb') as f:
            self.assertEqual(result, f.read())
