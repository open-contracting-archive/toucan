import json
import os.path
import re
from datetime import date
from io import BytesIO
from zipfile import ZipFile

from django.test import TestCase


def path(filename):
    return os.path.join('tests', 'fixtures', filename)


def read(filename, mode='rt', encoding=None, **kwargs):
    with open(path(filename), mode, encoding=encoding, **kwargs) as f:
        return f.read()


class ViewTestCase(TestCase):
    maxDiff = None

    def upload_and_go(self, upload_data=None, data=None, mode='r'):
        if upload_data is None:
            upload_data = {}
        if data is None:
            data = {}

        for file in self.files:
            with open(path(file), mode=mode) as f:
                upload_data['file'] = f
                self.client.post('/upload/', upload_data)

        response = self.client.get(self.url + 'go/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        content = json.loads(response.content.decode('utf-8'))
        return content

    def get_zipfile(self, content):
        response = self.client.get(content['url'])
        return ZipFile(BytesIO(response.getvalue()))

    def assertResults(self, upload_data, data, results, mode='r', has_warnings=False):
        content = self.upload_and_go(upload_data=upload_data, data=data, mode=mode)

        keys = ['url', 'size']
        if has_warnings:
            keys.append('warnings')

        for key in keys:
            self.assertIn(key, content.keys())
        self.assertEqual(len(content), len(keys))

        self.assertIsInstance(content['size'], int)
        self.assertRegex(content['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/$')

        zipfile = self.get_zipfile(content)
        names = zipfile.namelist()

        self.assertEqual(len(names), len(results))
        for name in names:
            part = next(part for pattern, part in results.items() if pattern == name or re.search(pattern, name))
            self.assertEqual(zipfile.read(name).decode('utf-8'), read(part))


class ViewTests:
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
