from unittest.mock import Mock, patch
from oauthlib.oauth2 import AccessDeniedError

from default import drive_options
from tests import ViewTestCase, ViewTests, path


class DriveTestCase(ViewTestCase, ViewTests):
    url = '/to-spreadsheet/'
    files = [
        '1.1/release-packages/0001-tender.json',
    ]

    @patch('google_auth_oauthlib.flow.InstalledAppFlow.run_local_server')
    @patch('default.drive_options.build')
    def test_go_with_files(self, mock_build, mock_run_local_server):
        mock_run_local_server.return_value.valid = True
        mock_build.return_value.files.return_value.create.return_value.execute.return_value = {'id': 1}
        contents = self.upload_and_go({'type': 'release-package'})

        for extension, content in contents.items():
            response = self.client.get(content['url'] + '?out=drive')
            self.assertEqual(response.status_code, 200)

    @patch('google_auth_oauthlib.flow.InstalledAppFlow.run_local_server')
    def test_invalid_credentials(self, mock_run_local_server):
        mock_run_local_server.return_value.valid = False
        contents = self.upload_and_go({'type': 'release-package'})

        response = self.client.get(contents['csv']['url'] + '?out=drive')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'UploadError')

    def test_refresh_fail(self):
        credentials = Mock(valid=False, expired=True, refresh_token='test')
        credentials.refresh = Mock(side_effect=AccessDeniedError())
        response = drive_options.upload_to_drive(
            filename="test",
            filepath=path(self.files[0]),
            format="json",
            credentials=credentials
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'AccessDeniedError')
