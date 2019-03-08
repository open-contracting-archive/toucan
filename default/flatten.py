import json
from libcove.lib.converters import convert_json
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.schema import SchemaOCDS

def flatten(input_file, uiid):
    upload_folder = '/tmp/algo/'
    upload_url = '/{}/'.format(str(uiid))
    lib_cove_config = LibCoveOCDSConfig()
    with open(input_file, 'r') as f:
        json_data = json.load(f, parse_float=Decimal)
        schema_ocds = SchemaOCDS(select_version='1.1', release_data = json_data, lib_cove_ocds_config = lib_cove_config)
