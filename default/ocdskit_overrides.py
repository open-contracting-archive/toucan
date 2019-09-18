import argparse
import io
import types
from contextlib import redirect_stdout
from datetime import datetime

from ocdskit.cli.commands import package_releases, compile


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


def command_package_releases(input_buffer, published_date=datetime.now().isoformat()):
    # TODO provide inputs for additional options
    namespace = argparse.Namespace(extension=None, pretty=False, ascii=False, uri='', publisher_name='',
                                   publisher_uri='', publisher_scheme='', publisher_uid='',
                                   published_date=published_date)
    return _execute_command(package_releases, input_buffer, namespace)


def command_compile(input_buffer, include_versioned=False, published_date=datetime.now().isoformat()):
    namespace = argparse.Namespace(pretty=False, ascii=False, schema=None, package=True, uri='', publisher_name='',
                                   publisher_uri='', publisher_scheme='', publisher_uid='',
                                   published_date=published_date, linked_releases=False, versioned=include_versioned)
    return _execute_command(compile, input_buffer, namespace)


if __name__ == '__main__':
    mybuffer = ['{"ocid": 1, "tag": ["planning"]}']
    with open('/tmp/test.txt', 'w') as myfile:
        myfile.write(command_package_releases(mybuffer))

    mybuffer = [
        '{\n"uri": "hola", "releases": [{"ocid": 1, "date": "2019-01-01", "tag": ["tender"], "tender": {"title": "hola"}}]}',  # noqa
        '{"uri": "hola", "releases": [{"ocid": 1, "date": "2019-01-01", "tag": ["award"], "awards": [{"status": "pending"}]}]}',  # noqa
    ]

    with open('/tmp/test_compile.txt', 'w') as myfile:
        myfile.write(command_compile(mybuffer))
