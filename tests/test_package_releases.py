from tests import ViewTestCase, ViewTests, PublishedDateTests


class PackageReleasesTestCase(ViewTestCase, ViewTests, PublishedDateTests):
    url = '/package-releases/'
    size = 1037
    size_with_published_date = 1049
    files = [
        '1.1/releases/0001-tender.json',
        '1.1/releases/0002-tender.json',
        '1.1/releases/0001-award.json',
    ]
