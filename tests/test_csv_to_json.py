from tests import ViewTestCase, ViewTests


class CsvToJsonTestCase(ViewTestCase, ViewTests):
    url = '/to-json/'
    files = [
        '1.1/spreadsheets/flattened.zip',
    ]

    def test_go_with_files(self):
        self.assertResults({'type': '.csv .xlsx .zip'}, {}, {
            'result.json': 'results/unflattened_csv.json',
        }, mode='rb')

        self.assertResults({'type': '.csv .xlsx .zip'}, {}, {
            'result.json': 'results/unflattened_csv.json',
        }, mode='rb')
