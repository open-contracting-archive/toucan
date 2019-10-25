import jsonref

from io import StringIO
from django.http.response import HttpResponse
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.schema import SchemaOCDS
from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method


def get_mapping_sheet_from_url(url):
    schema = jsonref.load_uri(url)

    return _get_mapping_sheet(schema)


def get_mapping_sheet_from_uploaded_file(uploaded):
    schema = jsonref.loads(uploaded.read())

    return _get_mapping_sheet(schema)


def get_extended_mapping_sheet(extensions):
    cove_config = LibCoveOCDSConfig()
    schema_ocds = SchemaOCDS('1.1', extensions, lib_cove_ocds_config=cove_config)
    json_schema = schema_ocds.get_release_schema_obj(deref=True)

    return _get_mapping_sheet(json_schema)


def _get_mapping_sheet(data):
    io = StringIO()

    mapping_sheet_method(data, io, infer_required=True)

    response = HttpResponse(io.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mapping-sheet.csv"'
    return response
