from tests import ViewTestCase, ViewTests


class UpgradeTestCase(ViewTestCase, ViewTests):
    url = '/upgrade/'
    size = 809
    files = [
        '1.0/release-packages/0001-tender.json',
    ]
