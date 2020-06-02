from tests import ViewTestCase, ViewTests


class SplitRecordPackageTestCase(ViewTestCase, ViewTests):
    url = '/split-packages/'
    files = [
        '1.1/record-packages/0001-record.json',
        '1.1/record-packages/0002-record.json',
        '1.1/record-packages/0003-record.json',
        '1.1/record-packages/0004-array-packages.json'
    ]

    def test_go_with_files(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'splitSize': '1', 'pretty-json': 'off',
                'encoding': 'utf-8', 'changePublishedDate': 'off'},
            {
                'result1.json': 'results/split-package/record/1/result1.json',
                'result2.json': 'results/split-package/record/1/result2.json',
                'result3.json': 'results/split-package/record/1/result3.json',
                'result4.json': 'results/split-package/record/1/result4.json',
                'result5.json': 'results/split-package/record/1/result5.json'
            },
        )

    def test_go_with_invalid_split_size(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'splitSize': '-1', 'pretty-json': 'off',
                'encoding': 'utf-8', 'changePublishedDate': 'off'},
            {
                'result1.json': 'results/split-package/record/1/result1.json',
                'result2.json': 'results/split-package/record/1/result2.json',
                'result3.json': 'results/split-package/record/1/result3.json',
                'result4.json': 'results/split-package/record/1/result4.json',
                'result5.json': 'results/split-package/record/1/result5.json'
            }, has_warnings=True
        )

    def test_go_with_valid_published_date_and_valid_split_size(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'splitSize': '1', 'changePublishedDate': 'on',
                'pretty-json': 'off', 'encoding': 'utf-8', 'publishedDate': '2001-02-03T00:00:00Z'},
            {
                'result1.json': 'results/split-package/record/2/result1.json',
                'result2.json': 'results/split-package/record/2/result2.json',
                'result3.json': 'results/split-package/record/2/result3.json',
                'result4.json': 'results/split-package/record/2/result4.json',
                'result5.json': 'results/split-package/record/2/result5.json'
            },
        )

    def test_go_with_valid_published_date_and_invalid_split_size(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'splitSize': '-1', 'changePublishedDate': 'on',
                'pretty-json': 'off', 'encoding': 'utf-8', 'publishedDate': '2001-02-03T00:00:00Z'},
            {
                'result1.json': 'results/split-package/record/2/result1.json',
                'result2.json': 'results/split-package/record/2/result2.json',
                'result3.json': 'results/split-package/record/2/result3.json',
                'result4.json': 'results/split-package/record/2/result4.json',
                'result5.json': 'results/split-package/record/2/result5.json'
            }, has_warnings=True
        )

    def test_go_with_invalid_published_date_and_invalid_split_size(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'record', 'splitSize': '-1', 'changePublishedDate': 'on',
                'pretty-json': 'off', 'encoding': 'utf-8', 'publishedDate': '2000-00-00T00:00:00Z'},
            {
                'result1.json': 'results/split-package/record/1/result1.json',
                'result2.json': 'results/split-package/record/1/result2.json',
                'result3.json': 'results/split-package/record/1/result3.json',
                'result4.json': 'results/split-package/record/1/result4.json',
                'result5.json': 'results/split-package/record/1/result5.json'
            }, has_warnings=True
        )
