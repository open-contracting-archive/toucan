from tests import ViewTestCase, ViewTests


class PackageReleasesTestCase(ViewTestCase, ViewTests):
    url = '/package-releases/'
    files = [
        '1.1/releases/0001-tender.json',
        '1.1/releases/0001-award.json',
        '1.1/releases/0002-tender.json',
    ]

    def test_go_with_files(self):
        self.assertResults({}, {
            'result.json': 'results/package-releases.json',
        })

    def test_go_with_valid_published_date(self):
        self.assertResults({'publishedDate': '2001-02-03T00:00:00Z'}, {
            'result.json': 'results/package-releases_published-date.json',
        })

    def test_go_with_invalid_published_date(self):
        self.assertResults({'publishedDate': '2000-00-00T00:00:00Z'}, {
            'result.json': 'results/package-releases.json',
        })
