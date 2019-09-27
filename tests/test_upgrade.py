from tests import ViewTestCase, ViewTests


class UpgradeTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    files = [
        '1.0/release-packages/0001-tender.json',
    ]

    def test_go_with_files(self):
        self.assertResults({}, {
            r'^0001-tender-[0-9a-f-]{36}-upgraded.json$': 'results/upgrade.json',
        })
