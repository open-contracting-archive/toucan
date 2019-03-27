import os
import flattentool
from zipfile import ZipFile, ZIP_DEFLATED
from flattentool.json_input import BadlyFormedJSONError
from libcoveocds.config import LibCoveOCDSConfig

def flatten(filename_handler, version='1.1'):
    lib_cove_config = LibCoveOCDSConfig()
    schema_url = lib_cove_config.config['schema_version_choices'][version][1] + 'release-schema.json'
    print(schema_url)

    folder = filename_handler.get_folder()
    flatten_kwargs = dict(
        output_name= os.path.join (folder, 'flatten-' + filename_handler.get_id()),
        main_sheet_name=lib_cove_config.config['root_list_path'],
        root_list_path=lib_cove_config.config['root_list_path'],
        root_id=lib_cove_config.config['root_id'],
        schema=schema_url,
        disable_local_refs=lib_cove_config.config['flatten_tool']['disable_local_refs'],
        remove_empty_schema_columns=lib_cove_config.config['flatten_tool']['remove_empty_schema_columns'],
        root_is_list=lib_cove_config.config.get('root_is_list', False),
        )
    
    flattentool.flatten(filename_handler.get_full_path(), **flatten_kwargs)

    # compress csv files
    zipfile_path = os.path.join(folder, 'flatten-csv-' + filename_handler.get_id() + '.zip')
    csv_folder = os.path.join(folder, 'flatten-' + filename_handler.get_id())
    with ZipFile(zipfile_path, 'w', compression=ZIP_DEFLATED) as myzip:
        for file in os.listdir(csv_folder):
            filename = os.fsdecode(file)
            myzip.write(os.path.join(csv_folder, filename), filename)
    
    # remove csv files
    for file in os.listdir(csv_folder):
        filename = os.fsdecode(file)
        os.remove(os.path.join(csv_folder, filename))
    os.rmdir(csv_folder)

