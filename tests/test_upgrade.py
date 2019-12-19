from tests import ViewTestCase, ViewTests


class UpgradeTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    files = [
        '1.0/record-packages/ocds-213czf-000-00001.json',
        '1.0/release-packages/0001-tender.json',
        '1.0/releases/0001-planning.json',
    ]

    def test_go_with_files(self):
        self.assertResults({'type': 'package release'}, {}, {
            r'^ocds-213czf-000-00001-[0-9a-f-]{36}-upgraded.json$': 'results/upgrade_record-package.json',
            r'^0001-tender-[0-9a-f-]{36}-upgraded.json$': 'results/upgrade_release-package.json',
            r'^0001-planning-[0-9a-f-]{36}-upgraded.json$': 'results/upgrade_release.json',
        })
