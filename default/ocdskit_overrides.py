import io
import types
import argparse
from contextlib import redirect_stdout
from ocdskit.cli.commands import package_releases, compile, mapping_sheet

def _execute_command(package, input_buffer, namespace):
    def buffer(self):
        return input_buffer

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand')

    command = package.Command(subparsers)
    command.args = namespace
    command.buffer = types.MethodType(buffer, command)
    
    f = io.StringIO()
    with redirect_stdout(f):
        command.handle()

    return f.getvalue()

def command_package_releases(input_buffer):
    namespace = argparse.Namespace(extension=None, pretty=False, ascii=False)
    return _execute_command(package_releases, input_buffer, namespace)

def command_compile(input_buffer, include_versioned=False):
    namespace = argparse.Namespace(pretty=False, ascii=False, schema=None, package=True, uri='', published_date='', linked_releases=False, versioned=include_versioned)
    return _execute_command(compile, input_buffer, namespace)

def command_mapping_sheet(input_buffer):
    namespace = argparse.Namespace(pretty=False,ascii=False)
    return _execute_command(mapping_sheet, input_buffer, namespace)

if __name__ == '__main__':
    mybuffer = ['{"ocid": 1, "tag": ["planning"]}']
    with open('/tmp/test.txt', 'w') as myfile:
        myfile.write(command_package_releases(mybuffer))

    mybuffer =  ['{\n"uri": "hola", "releases": [{"ocid": 1, "date": "2019-01-01", "tag": ["tender"], "tender": {"title": "hola"}}]}',\
        '{"uri": "hola", "releases": [{"ocid": 1, "date": "2019-01-01", "tag": ["award"], "awards": [{"status": "pending"}]}]}']

    with open('/tmp/test_compile.txt', 'w') as myfile:
        myfile.write(command_compile(mybuffer))
