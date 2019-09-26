from datetime import date

from django.test import TestCase

from default.tests import ViewTests


class UpgradeTestCase(TestCase, ViewTests):
    url = '/upgrade/'
    files = [
        '1.0/release-packages/0001-tender.json',
    ]

    def test_go(self):
        content = self.upload_and_go()

        self.assertEqual(len(content), 2)
        self.assertEqual(content['size'], 809)
        self.assertRegex(content['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/$')
