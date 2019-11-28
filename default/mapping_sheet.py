from io import StringIO

import jsonref
from django.http.response import HttpResponse
from ocdsextensionregistry import ProfileBuilder
from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method


def get_mapping_sheet_from_url(url):
    schema = jsonref.load_uri(url)
    return _get_mapping_sheet(schema)


def get_mapping_sheet_from_uploaded_file(uploaded):
    schema = jsonref.load(uploaded)
    return _get_mapping_sheet(schema)


def get_extended_mapping_sheet(extensions, version):
    builder = ProfileBuilder(version, extensions)
    schema = jsonref.JsonRef.replace_refs(builder.patched_release_schema())
    return _get_mapping_sheet(schema)


def _get_mapping_sheet(data):
    io = StringIO()
    mapping_sheet_method(data, io, infer_required=True)

    response = HttpResponse(io.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mapping-sheet.csv"'

    return response
