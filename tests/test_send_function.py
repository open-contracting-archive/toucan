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
