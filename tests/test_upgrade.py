from tests import ViewTestCase, ViewTests


class UpgradeTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    files = [
        '1.0/release-packages/0001-tender.json',
    ]
    results = {
        r'^0001-tender-[0-9a-f-]{36}_updated.json$': 'results/upgrade.json',
    }
