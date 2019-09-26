from datetime import date

from tests import ViewTestCase, ViewTests


class ToSpreadsheetTestCase(ViewTestCase, ViewTests):
    url = '/to-spreadsheet/'
    files = [
        '1.1/release-packages/0001-tender.json',
    ]

    def test_go_with_files(self):
        content = self.upload_and_go()

        self.assertEqual(len(content), 2)
        self.assertEqual(len(content['csv']), 2)
        self.assertEqual(len(content['xlsx']), 2)
        self.assertEqual(content['csv']['size'], 946)
        self.assertRegex(content['csv']['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/csv/$')
        self.assertAlmostEqual(content['xlsx']['size'], 6362, delta=1)
        self.assertRegex(content['xlsx']['url'], r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/xlsx/$')
