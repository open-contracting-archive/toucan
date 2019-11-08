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
        self.assertResults({'packageType': 'release'}, {
            'result.json': 'results/combine_release_packages.json',
        })

    def test_go_with_valid_published_date(self):
        self.assertResults({'packageType': 'release', 'publishedDate': '2001-02-03T00:00:00Z'}, {
            'result.json': 'results/combine_release_packages-date.json',
        })

    def test_go_with_invalid_published_date(self):
        self.assertResults({'packageType': 'release', 'publishedDate': '2000-00-00T00:00:00Z'}, {
            'result.json': 'results/combine_release_packages.json',
        })