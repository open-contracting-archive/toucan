import json
import re
from datetime import date
from zipfile import ZipFile

from tests import ViewTestCase, ViewTests, path, read


class ToSpreadsheetTestCase(ViewTestCase, ViewTests):
    url = '/to-spreadsheet/'

    def assertPostResults(self, results, options, csv_path=None, xlsx_path=None):
        contents = self.upload_and_go({'type': 'release-package'}, method='post', data=options)

        self.assertEqual(len(contents), len(results))

        prefix = r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/'

        for extension, content in contents.items():
            self.assertEqual(len(content), 3)
            self.assertIsInstance(content['size'], int)
            self.assertRegex(content['url'], prefix + extension + ('.zip' if extension == 'csv' else '') + r'/$')

        if csv_path:
            zipfile = self.get_zipfile(contents['csv'])

            self.assertEqual(len(zipfile.namelist()), len(results['csv']))
            for name in results['csv']:
                self.assertEqual(zipfile.read(name).decode('utf-8').replace('\r\n', '\n'),
                                 read(csv_path + name))

        if xlsx_path:
            actual = self.get_zipfile(contents['xlsx'])
            with open(path(xlsx_path), 'rb') as f:
                expected = ZipFile(f)

                self.assertEqual(_worksheets_length(actual), _worksheets_length(expected))
                for name in results['xlsx']:
                    self.assertEqual(actual.read(name), expected.read(name))

    def test_go_with_files(self):
        self.files = [
            '1.1/release-packages/0001-tender.json',
        ]

        results = {
            'csv': [
                'releases.csv',
                'ten_items.csv',
                'parties.csv',
            ],
            'xlsx': [
                'xl/worksheets/sheet1.xml',
                'xl/worksheets/sheet2.xml',
                'xl/worksheets/sheet3.xml',
            ]
        }

        options = {
            'schema': 'https://standard.open-contracting.org/1.1/en/release-schema.json',
            'output_format': ['csv', 'xlsx'],
            'use_titles': 'False',
            'remove_empty_schema_columns': 'True'
        }

        self.assertPostResults(results, options, csv_path='results/flattened/', xlsx_path='results/flattened.xlsx')

    def test_flatten_options(self):
        self.files = [
            '1.1/release-packages/ocds-213czf-000-00001.json',
        ]

        results = {
            'xlsx': [
                'xl/worksheets/sheet1.xml'
            ]
        }

        options = {
            'schema': 'https://standard.open-contracting.org/1.1/en/release-schema.json',
            'output_format': ['xlsx'],
            'use_titles': 'True',
            'filter_field': 'ocid',
            'filter_value': 'ocds-213czf-000-00001',
            'preserve_fields': ['ocid',
                                'id',
                                'date',
                                'tag',
                                'initiationType',
                                'buyer/name',
                                'buyer/id',
                                'planning/rationale',
                                'planning/budget/description',
                                'planning/budget/amount/amount',
                                'planning/budget/amount/currency'],
            'remove_empty_schema_columns': 'True'
        }

        self.assertPostResults(results, options, xlsx_path='results/flattened-with-options.xlsx')

    def test_validation_errors(self):
        file = 'tests/fixtures/1.1/release-packages/ocds-213czf-000-00001.json'

        options = {
            'filter_field': 'ocid'
        }

        response_expected = {
            'form_errors': {
                'schema': ['This field is required.'],
                'output_format': ['This field is required.'],
                'use_titles': ['This field is required.'],
                'remove_empty_schema_columns': ['This field is required.'],
                'filter_field': ['Define both the field and value to filter data']
            }
        }

        with open(file) as fd:
            response = self.client.post('/upload/', {'file': fd, 'type': 'release-package'})
            self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url + 'go/', data=options)
        self.assertEqual(response.status_code, 400)

        content = response.content.decode('utf-8')

        self.assertEqual(json.dumps(response_expected), content)

    def test_get_schema_options(self):
        options_url = self.url + 'get-schema-options'
        data = {
            'url': 'https://standard.open-contracting.org/1.1/en/release-schema.json'
        }

        response = self.client.get(options_url, data)
        self.assertEqual(response.status_code, 200)

        contents = re.sub(r'\s+', ' ', response.content.decode('utf-8'))

        # ocid is a top-level, required element which should be selected and disabled
        self.assertInHTML(
            '<li data-jstree=\'{ "selected": true, "icon": "glyphicon glyphicon-minus", "disabled": true }\' '
            'data-path="ocid">ocid</li>',
            contents)

        # parties is a top-level element, should be selected by default
        self.assertIn(
            '<li data-jstree=\'{ "selected": true, "icon": "glyphicon glyphicon-th-list" }\' data-path="parties" > '
            'parties <ul>',
            contents)

        # identifier is not a top-level field, so it does not have any special attributes
        self.assertIn(
            '<li data-jstree=\'{ "icon": "glyphicon glyphicon-th-list" }\' data-path="parties/identifier" > '
            'identifier <ul>',
            contents)

    def test_get_schema_options_fail(self):
        options_url = self.url + 'get-schema-options'

        expected_response = {
            'error': 'The url parameter is required'
        }

        response = self.client.get(options_url)
        self.assertEqual(response.status_code, 400)
        contents = response.content.decode('utf-8')
        self.assertEqual(json.dumps(expected_response), contents)

        data = {
            'url': 'invalid-url'
        }

        response = self.client.get(options_url, data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content.decode('utf-8'), 'There was an error retrieving the schema requested')


def _worksheets_length(zipfile):
    return len([name for name in zipfile.namelist() if name.startswith('xl/worksheets')])
