import jsonref
import requests

from io import StringIO
from django.http.response import HttpResponse
from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method
from django.core.cache import cache
from ocdsextensionregistry import ProfileBuilder

CACHE_KEY = 'git_tags'
CACHE_TIMEOUT = 3600


def get_mapping_sheet_from_url(url):
    schema = jsonref.load_uri(url)

    return _get_mapping_sheet(schema)


def get_mapping_sheet_from_uploaded_file(uploaded):
    schema = jsonref.loads(uploaded.read())

    return _get_mapping_sheet(schema)


def get_extended_mapping_sheet(extensions, version='1__1__4'):
    builder = ProfileBuilder(version, extensions)

    return _get_mapping_sheet(jsonref.JsonRef.replace_refs(builder.patched_release_schema()))


def _get_mapping_sheet(data):
    io = StringIO()

    mapping_sheet_method(data, io, infer_required=True)

    response = HttpResponse(io.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mapping-sheet.csv"'
    return response


def get_standard_tags():
    if cache.get(CACHE_KEY) is None:
        github_res = requests.get('https://api.github.com/repos/open-contracting/standard/tags')
        if github_res.status_code == 200:
            cache.set(CACHE_KEY, [tag['name'] for tag in github_res.json()], timeout=CACHE_TIMEOUT)
        else:
            raise ValueError('Standard tags information is not available')
    return cache.get(CACHE_KEY)
