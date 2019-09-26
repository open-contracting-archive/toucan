from datetime import date

from django.test import TestCase

from default.tests import ViewTests


class PackageReleasesTestCase(TestCase, ViewTests):
    url = '/package-releases/'
    files = [
        '1.1/releases/0001-tender.json',
        '1.1/releases/0002-tender.json',
        '1.1/releases/0001-award.json',
    ]

    def test_go(self):
        content = self.upload_and_go()

        self.assertEqual(len(content), 2)
        self.assertEqual(content['size'], 1037)
        self.assertRegex(content['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/$')
