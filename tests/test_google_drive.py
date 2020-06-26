import json
from datetime import datetime

from unittest.mock import patch

from tests import ViewTestCase, ViewTests


class DriveTestCase(ViewTestCase, ViewTests):
    url = '/to-spreadsheet/'
    files = [
        '1.1/release-packages/0001-tender.json',
    ]

    def _test_base(self, auth_response_success=True):
        # run the transformation as usual
        file_response = self.upload_and_go({'type': 'release-package'})
        self.assertIn('xlsx', file_response.keys())
        self.assertIn('driveUrl', file_response['xlsx'].keys())

        # call the google drive save request
        response = self.client.get(file_response['xlsx']['driveUrl'])
        contents = json.loads(response.content.decode('utf-8'))

        # no user authenticated yet
        self.assertIn('authenticated', contents.keys())
        self.assertEqual(contents['authenticated'], False)

        # call the query status method
        response = self.client.get('/google-drive-save-status')
        contents = json.loads(response.content.decode('utf-8'))

        self.assertEqual(contents['status'], 'waiting')

        # call the auth response method, this always return a page with a simple text message
        if auth_response_success:
            response = self.client.get('/googleapi-auth-response?code=test')
        else:
            response = self.client.get('/googleapi-auth-response?error=access_denied')
        self.assertIn('The authentication has finished, you can close this window now.',
                      response.content.decode('utf-8'))

        return file_response

    def _clear_credentials(self):
        if 'credentials' in self.client.session:
            del self.client.session['credentials']
            self.client.session.save()

    @patch('default.google_drive.Flow.from_client_secrets_file')
    @patch('default.google_drive.build')
    @patch('default.google_drive.Credentials.refresh')
    def test_go_with_files(self, mock_refresh, mock_build, mock_flow):
        mock_build.return_value.files.return_value.create.return_value.execute.return_value = {'id': '101'}
        test_credentials = {
            'token': 'token_test',
            'refresh_token': 'refresh_token_test',
            'id_token': 'id_token_test',
            'token_uri': 'token_uri_test',
            'client_id': 'client_id_test',
            'client_secret': 'client_secret_test',
            'scopes': 'scopes_test',
            'expiry': datetime.now(),
        }
        mock_flow.return_value.credentials.configure_mock(**test_credentials)

        file_response = self._test_base()

        # call the query status method, this calls the drive class
        response = self.client.get('/google-drive-save-status')
        contents = json.loads(response.content.decode('utf-8'))

        self.assertEqual(contents['authenticated'], True)
        self.assertEqual(contents['status'], 'success')
        self.assertEqual(contents['url'], 'https://drive.google.com/file/d/101')

        # test token refresh
        response = self.client.get(file_response['csv']['driveUrl'])
        contents = json.loads(response.content.decode('utf-8'))

        self.assertTrue(mock_refresh.called)
        self.assertEqual(contents['authenticated'], True)
        self.assertEqual(contents['status'], 'success')
        self.assertEqual(contents['url'], 'https://drive.google.com/file/d/101')

    def test_auth_failure(self):
        self._clear_credentials()
        self._test_base(auth_response_success=False)

        # call the query status method
        response = self.client.get('/google-drive-save-status')
        self.assertEqual(response.status_code, 500)
        contents = json.loads(response.content.decode('utf-8'))

        self.assertEqual(contents['status'], 'failed')
        self.assertEqual(contents['message'],
                         'There was an authorization issue when saving the file to Google Drive, please try again.')

    @patch('default.google_drive.Flow.from_client_secrets_file')
    def test_save_failure(self, mock_flow):
        mock_flow.return_value.fetch_token.side_effect = Exception('Invalid credentials')

        self._clear_credentials()
        self._test_base()

        # call the query status method
        response = self.client.get('/google-drive-save-status')
        self.assertEqual(response.status_code, 500)
        contents = json.loads(response.content.decode('utf-8'))

        self.assertEqual(contents['status'], 'failed')
        self.assertEqual(contents['message'],
                         'There was an issue when trying to upload the file to Google Drive, please try again later.')

    def test_query_status_failure(self):
        response = self.client.get('/google-drive-save-status')

        self.assertEqual(response.status_code, 400)
        contents = json.loads(response.content.decode('utf-8'))
        self.assertEqual(contents['error'], True)
        self.assertEqual(contents['message'], 'Invalid request, authentication process has not been started.')
