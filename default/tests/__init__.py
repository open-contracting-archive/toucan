import json
import os.path


def path(filename):
    return os.path.join('default', 'tests', 'fixtures', filename)


def read(filename, mode='rt', encoding=None, **kwargs):
    with open(path(filename), mode, encoding=encoding, **kwargs) as f:
        return f.read()


class ViewTests:
    def upload_and_go(self):
        for file in self.files:
            with open(path(file)) as f:
                response = self.client.post('/upload/', {'file': f})

        response = self.client.get(self.url + 'go/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        content = json.loads(response.content.decode('utf-8'))
        return content

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_go_without_files(self):
        response = self.client.get(self.url + 'go/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason_phrase, 'No files available for operation')
        self.assertEqual(response['Content-Type'], 'application/json')

        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content, {
            'error': 'No files uploaded',
        })
