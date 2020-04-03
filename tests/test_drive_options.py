from unittest.mock import Mock

from default import drive_options

from tests import ViewTestCase, ViewTests, path


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

    def test_access_denied(self):
        credentials = Mock(valid=False, expired=False, refresh_token='test')
        response = drive_options.upload_to_drive(
            filename="test",
            filepath="test",
            test=True,
            credentials=credentials
        )
        self.assertEqual(response.status_code, 400)

    def test_fail_uploading(self):
        credentials = Mock(valid=False, expired=True, refresh_token='test')
        for file in self.files:
            response = drive_options.upload_to_drive(
                filename="test",
                filepath=path(file),
                format="json",
                credentials=credentials
            )
            self.assertEqual(response.status_code, 400)
