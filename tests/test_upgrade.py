from tests import ViewTestCase, ViewTests


class UpgradeTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    files = [
        '1.0/release-packages/0001-tender.json',
    ]
