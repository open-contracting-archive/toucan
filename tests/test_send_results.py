from tests import ViewTestCase, ViewTests


class SendTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    send_to_url = '/combine-packages/go/?packageType=release&sendResult=true&type=release-package'
    files = [
        '1.0/release-packages/0001-tender.json',
    ]

    def test_send_result(self):
        self.url = '/upgrade/'
        content = self.upload_and_go({'type': 'release-package'})

        response = self.client.get(content['url'], data={'sendResult': 'true'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/send-result/validate/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.send_to_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_send_result_error(self):
        response = self.client.get('/send-result/validate/')
        self.assertEqual(response.status_code, 400)

    def test_send_result_invalid_type(self):
        self.url = '/compile/'
        content = self.upload_and_go({'type': 'release-package'})

        response = self.client.get(content['url'], data={'sendResult': 'true'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.send_to_url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, b'Not a release package')
