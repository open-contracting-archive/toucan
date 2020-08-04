import json
import os.path

from django.test import TestCase

from tests import path


class FileUploadTestCase(TestCase):
    def assertSuccess(self, filename, file_type):
        filepath = path(filename)
        with open(filepath) as f:
            response = self.client.post('/upload/', {'file': f, 'type': file_type})

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')

            content = json.loads(response.content.decode('utf-8'))

            self.assertEqual(len(content), 1)
            self.assertEqual(len(content['files']), 1)
            self.assertEqual(len(content['files'][0]), 3)

            self.assertRegex(content['files'][0]['id'], r'^[0-9a-f-]{36}$')
            self.assertEqual(content['files'][0]['name'], os.path.basename(f.name))
            self.assertEqual(content['files'][0]['size'], os.path.getsize(filepath))

    def assertError(self, file_type, message):
        with open(path('object.json')) as f:
            response = self.client.post('/upload/', {'file': f, 'type': file_type})

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.content.decode('utf-8'), message)

    def test_fail(self):
        with open(path('empty.json')) as f:
            response = self.client.post('/upload/', {'file': f, 'type': 'release-package'})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode('utf-8'), 'Error decoding JSON')

    def test_delete_file(self):
        with open(path('1.1/releases/0001-award.json')) as f:
            response = self.client.post('/upload/', {'file': f, 'type': 'release release-array'})

        content = json.loads(response.content.decode('utf-8'))
        file_id = content['files'][0]['id']

        response = self.client.get('/delete/' + file_id)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message'], 'File deleted')

        response = self.client.get('/delete/' + file_id)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(content['message'], 'File not found')

        session = self.client.session
        del session['files']
        session.save()

        response = self.client.get('/delete/' + file_id)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(content['message'], 'File not found')

    def test_record_package_success(self):
        self.assertSuccess('1.1/record-packages/0001-record.json', 'record-package')

    def test_release_package_success(self):
        self.assertSuccess('1.1/release-packages/0001-award.json', 'release-package')

    def test_package_success(self):
        filenames = [
            '1.1/record-packages/0001-record.json',
            '1.1/record-packages/0004-array-packages.json',
            '1.1/release-packages/0001-tender.json',
            '1.1/release-packages/0003-array-packages.json',
        ]
        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertSuccess(filename, 'package package-array')

    def test_release_success(self):
        filenames = [
            '1.1/releases/0001-tender.json',
            '1.1/releases/0003-array-tender.json',
        ]
        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertSuccess(filename, 'release release-array')

    def test_record_package_error(self):
        self.assertError('record-package', 'Not a record package')

    def test_release_package_error(self):
        self.assertError('release-package', 'Not a release package')

    def test_package_error(self):
        self.assertError('package package-array', 'Not a package or list of packages')

    def test_release_error(self):
        self.assertError('release release-array', 'Not a release or list of releases')
