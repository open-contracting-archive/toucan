from tests import ViewTestCase, ViewTests, PublishedDateTests


class PackageReleasesTestCase(ViewTestCase, ViewTests, PublishedDateTests):
    url = '/package-releases/'
    files = [
        '1.1/releases/0001-tender.json',
        '1.1/releases/0001-award.json',
        '1.1/releases/0002-tender.json',
    ]
    results = {
        'result.json': 'results/package-releases.json',
    }
