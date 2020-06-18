import json

from tests import ViewTestCase, ViewTests


class SendTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    send_to_url = '/to-spreadsheet/'
    files = [
        '1.0/release-packages/0001-tender.json'
    ]

    def test_send_result_to_function(self):
        self.url = '/upgrade/'
        content = self.upload_and_go({'type': 'release-package'})

        response = self.client.get(content['url'] + '?destination=function')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.send_to_url + 'go/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_add_multiple_results(self):
        self.url = '/to-spreadsheet/'
        contents = self.upload_and_go({'type': 'release-package'})

        for extension, content in contents.items():
            response = self.client.get(content['url'] + '?destination=function')
            self.assertEqual(response.status_code, 200)

    def test_receive_result(self):
        self.url = '/upgrade/'
        content = self.upload_and_go({'type': 'release-package'})

        response = self.client.get(content['url'] + '?destination=function')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/result/receive/?type=release-package')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_data.get('receive_result'), True)

        response = self.client.get('/result/receive/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"receive_result": false}')

    def test_receive_result_invalid_type(self):
        self.url = '/package-releases/'
        content = self.upload_and_go({'type': 'release-package'})

        response = self.client.get(content['url'] + '?destination=function')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/result/receive/?type=release release-array')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Not a release or list of releases')

    def test_not_receive_result(self):
        response = self.client.get('/result/receive/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"receive_result": false}')
