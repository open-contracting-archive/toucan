from unittest.mock import Mock, patch

from django.test import TestCase


class UploadUrlTestCase(TestCase):
    urls = [
        'http://example.com',
        'http://example2.com',
        'http://example3.com',
        'badurl'
    ]

    def test_upload_url(self):
        response = self.client.post('/upload-url/', {'input_url': self.urls[0]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_fail_upload_multiple_urls(self):
        response = self.client.post('/upload-url/', {'input_url': self.urls})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    @patch('default.views.os')
    def test_folder_creation(self, mock_os):
        mock_os.stat = Mock(side_effect=FileNotFoundError())
        mock_os.mkdir = Mock(side_effect=FileNotFoundError())
        with self.assertRaises(FileNotFoundError):
            self.client.post('/upload-url/', {'input_url': self.urls[0]})
