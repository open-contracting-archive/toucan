from datetime import date

from tests import ViewTestCase, ViewTests, PublishedDateTests


class CompileTestCase(ViewTestCase, ViewTests, PublishedDateTests):
    url = '/compile/'
    files = [
        '1.1/release-packages/0001-tender.json',
        '1.1/release-packages/0001-award.json',
        '1.1/release-packages/0002-tender.json',
    ]
    results = {
        'result.json': 'results/compile.json',
    }

    def test_go_with_include_versioned(self):
        content = self.upload_and_go({'includeVersioned': 'true'})

        self.assertEqual(len(content), 2)
        self.assertIsInstance(content['size'], int)
        self.assertRegex(content['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/$')
