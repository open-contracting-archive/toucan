from tests import ViewTestCase, ViewTests


class CombineRecordPackageTestCase(ViewTestCase, ViewTests):
    url = '/combine-packages/'
    files = [
        '1.1/record-packages/0001-record.json',
        '1.1/record-packages/0002-record.json',
        '1.1/record-packages/0003-record.json',
        '1.1/record-packages/0004-array-packages.json',
    ]

    def test_go_with_files(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record'},
            {'result.json': 'results/combine_record_packages.json'},
        )

    def test_go_with_valid_published_date(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'publishedDate': '2001-02-03T00:00:00Z'},
            {'result.json': 'results/combine_record_packages-date.json'},
        )

    def test_go_with_invalid_published_date(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'publishedDate': '2000-00-00T00:00:00Z'},
            {'result.json': 'results/combine_record_packages.json'},
            has_warnings=True,
        )
