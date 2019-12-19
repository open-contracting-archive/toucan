from tests import ViewTestCase, ViewTests


class XlsxToJsonTestCase(ViewTestCase, ViewTests):
    url = '/to-json/'
    files = [
        '1.1/spreadsheets/flattened.xlsx',
    ]

    def test_go_with_files(self):
        self.assertResults({'type': 'xlsx zip'}, {}, {
            'result.json': 'results/unflattened_xlsx.json',
        }, mode='rb')
