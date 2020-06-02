from tests import ViewTestCase, ViewTests


class CompileTestCase(ViewTestCase, ViewTests):
    url = '/compile/'
    files = [
        '1.1/release-packages/0001-tender.json',
        '1.1/release-packages/0001-award.json',
        '1.1/release-packages/0002-tender.json',
    ]

    def test_go_with_files(self):
        self.assertResults(
            {'type': 'release-package'},
            {'pretty-json': 'off', 'encoding': 'utf-8'},
            {'result.json': 'results/compile.json', }
        )

    def test_go_with_valid_published_date(self):
        self.assertResults(
            {'type': 'release-package'},
            {'pretty-json': 'off', 'encoding': 'utf-8',
                'publishedDate': '2001-02-03T00:00:00Z'},
            {'result.json': 'results/compile_published-date.json', }
        )

    def test_go_with_invalid_published_date(self):
        self.assertResults(
            {'type': 'release-package'},
            {'pretty-json': 'off', 'encoding': 'utf-8',
                'publishedDate': '2000-00-00T00:00:00Z'},
            {'result.json': 'results/compile.json', },
            has_warnings=True
        )

    def test_go_with_include_versioned(self):
        self.assertResults(
            {'type': 'release-package'},
            {'pretty-json': 'off', 'encoding': 'utf-8',
                'includeVersioned': 'true'},
            {'result.json': 'results/compile_versioned.json', }
        )
