import json

from django.test import TestCase
from tests import path


class FileUploadTestCase(TestCase):

    empty_file = 'empty.json'
    file_to_delete = '1.1/releases/0001-award.json'

    release_package_file = '1.1/release-packages/0001-award.json'
    record_package_file = '1.0/record-packages/134721.json'

    def test_upload_file(self):
        with open(path(self.empty_file)) as f:
            response = self.client.post('/upload/', {'file': f})

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.content.decode('utf-8'), "Error decoding json")

    def test_delete_file(self):
        with open(path(self.file_to_delete)) as f:
            response = self.client.post('/upload/', {'file': f})
            content = json.loads(response.content.decode('utf-8'))
            file_id = content['files'][0]['id']

            response = self.client.get('/delete/' + file_id)
            content = json.loads(response.content.decode('utf-8'))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(content['message'], 'File deleted')

            response = self.client.get('/delete/' + file_id)
            self.assertEqual(response.status_code, 400)
            content = json.loads(response.content.decode('utf-8'))

            self.assertEqual(content['message'], 'File not found')

            session = self.client.session
            del session['files']
            session.save()

            response = self.client.get('/delete/' + file_id)
            self.assertEqual(response.status_code, 400)
            content = json.loads(response.content.decode('utf-8'))

            self.assertEqual(content['message'], 'No files to delete')

    def test_file_validations(self):
        with open(path(self.release_package_file)) as f:
            response = self.client.post('/upload/', {'file': f, 'validateType': 'release-package'})
            self.assertEqual(response.status_code, 200)

            f.seek(0)
            response = self.client.post('/upload/', {'file': f, 'validateType': 'record-package'})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.content.decode('utf-8'), 'Not a record package')

        with open(path(self.record_package_file)) as f:
            response = self.client.post('/upload/', {'file': f, 'validateType': 'record-package'})
            self.assertEqual(response.status_code, 200)

            f.seek(0)
            response = self.client.post('/upload/', {'file': f, 'validateType': 'release-package'})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.content.decode('utf-8'), 'Not a release package')
