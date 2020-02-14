from tests import ViewTestCase, ViewTests


class DriveTestCase(ViewTestCase, ViewTests):
    url = '/to-spreadsheet/'
    files = [
        '1.1/release-packages/0001-tender.json',
    ]

    def test_go_with_files(self):
        contents = self.upload_and_go({'type': 'release-package'})

        for extension, content in contents.items():
            response = self.client.get(content['url'] + '?out=drive&test=true')
            self.assertEqual(response.status_code, 200)
