from tests import ViewTestCase, ViewTests


class OneCsvToJsonTestCase(ViewTestCase, ViewTests):
    url = '/to-json/'
    files = [
        '1.1/spreadsheets/flattened.csv',
    ]

    def test_go_with_files(self):
        self.assertResults({'type': '.csv .xlsx .zip'}, {}, {
            'result.json': 'results/unflattened_one_csv.json',
        }, mode='rb')
