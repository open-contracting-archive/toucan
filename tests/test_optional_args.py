from tests import ViewTestCase, ViewTests


class OptionalArgsTestCase(ViewTestCase, ViewTests):
    url = '/package-releases/'
    files = [
        '1.1/releases/0001-tender.json',
        '1.1/releases/0001-award.json',
        '1.1/releases/0002-tender.json',
        '1.1/releases/0003-array-tender.json',
    ]

    def test_go_with_not_checked_pretty_json(self):
        self.assertResults(
            {'type': 'release release-array'},
            {'pretty-json': 'false'},
            {'result.json': 'results/package-releases.json', }
        )

    def test_go_with_checked_pretty_json(self):
        self.assertResults(
            {'type': 'release release-array'},
            {'pretty-json': 'true'},
            {'result.json': 'results/optional-args/package-releases_pretty_json.json', }
        )

    def test_go_with_valid_encoding(self):
        self.assertResults(
            {'type': 'release release-array'},
            {'encoding': 'utf-8'},
            {'result.json': 'results/package-releases.json', }
        )

    def test_go_with_invalid_encoding(self):
        self.assertResults(
            {'type': 'release release-array'},
            {'encoding': 'none'},
            {'result.json': 'results/package-releases.json', },
            has_warnings=True,
            warnings=['Encoding none ... is not recognized. The default value \'utf-8\' was used.']
        )

    def test_multiple_warnings(self):
        content = self.upload_and_go(
            upload_data={'type': 'release release-array'},
            data={'encoding': 'none', 'publishedDate': '2000-00-00T00:00:00Z'}, mode='r'
        )
        self.assertEqual(
            content['warnings'],
            [
                'An invalid published date was submitted, and therefore ignored: 2000-00-00T00:00:00Z',
                'Encoding none ... is not recognized. The default value \'utf-8\' was used.'
            ]
        )
