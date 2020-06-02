from tests import ViewTestCase, ViewTests


class CombineReleasePackageTestCase(ViewTestCase, ViewTests):
    url = '/combine-packages/'
    files = [
        '1.1/release-packages/0001-tender.json',
        '1.1/release-packages/0001-award.json',
        '1.1/release-packages/0002-tender.json',
        '1.1/release-packages/0003-array-packages.json',
    ]

    def test_go_with_files(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'release', 'pretty-json': 'off', 'encoding': 'utf-8'},
            {'result.json': 'results/combine_release_packages.json'},
        )

    def test_go_with_valid_published_date(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'release', 'pretty-json': 'off',
                'encoding': 'utf-8', 'publishedDate': '2001-02-03T00:00:00Z'},
            {'result.json': 'results/combine_release_packages-date.json'},
        )

    def test_go_with_invalid_published_date(self):
        self.assertResults(
            {'type': 'package package-array'},
            {'packageType': 'release', 'pretty-json': 'off',
                'encoding': 'utf-8', 'publishedDate': '2000-00-00T00:00:00Z'},
            {'result.json': 'results/combine_release_packages.json'},
            has_warnings=True,
        )
