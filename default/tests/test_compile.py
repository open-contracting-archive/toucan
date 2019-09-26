from datetime import date

from default.tests import ViewTestCase, ViewTests, PublishedDateTests


class CompileTestCase(ViewTestCase, ViewTests, PublishedDateTests):
    url = '/compile/'
    size = 651
    size_with_published_date = 651
    files = [
        '1.1/release-packages/0001-tender.json',
    ]

    def test_go_with_include_versioned(self):
        content = self.upload_and_go({'includeVersioned': 'true'})

        self.assertEqual(len(content), 2)
        self.assertEqual(content['size'], 714)
        self.assertRegex(content['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/$')
