from unittest.mock import Mock, patch

from django.test import TestCase


class UploadUrlTestCase(TestCase):
    url = 'http://example.com'

    @patch('default.views.os')
    def test_upload_url(self, mock_os):
        mock_os.stat = Mock(side_effect=FileNotFoundError())
        response = self.client.post('/upload-url/', {'input_url': self.url})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_bad_url(self):
        bad_url = self.url.replace('.', "")
        response = self.client.post('/upload-url/', {'input_url': bad_url})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('utf-8'), bad_url)
