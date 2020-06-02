import json
import os
import uuid
from datetime import date
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from ocdskit.util import json_dumps


class DataFile:
    """
    A data file on the server, that was either uploaded by a user or generated in response to a request.
    """

    """
    The separator between the prefix and ID of the file.
    """
    sep = '-'

    def __init__(self, prefix, ext, id=None, folder=None):
        if len(prefix) > 20:
            prefix = prefix[:20 + 1]

        self.prefix = prefix
        self.ext = ext
        self.id = id or str(uuid.uuid4())

        if folder is not None:
            self.folder = folder
        else:
            self.folder = '{:%Y-%m-%d}'.format(date.today())

    def __repr__(self):
        return '{0.folder}/{0.prefix}{0.sep}{0.id}{0.ext}'.format(self)

    def as_dict(self):
        return self.__dict__

    def name_with_suffix(self, suffix):
        """
        Returns the file's name, with a suffix before its extension.

        :param str suffix: a suffix to the file's name
        """
        return self.prefix + self.sep + self.id + self.sep + suffix + self.ext

    @property
    def path(self):
        """
        Returns the full path to the file.
        """
        return os.path.join(self._directory, self._name)

    @property
    def url(self):
        """
        Returns the URL path to the file.
        """
        return '/result/{}/{}/'.format(self.folder, self.id)

    @property
    def size(self):
        """
        Returns the size of the file.
        """
        return os.path.getsize(self.path)

    def json(self, **kwargs):
        """
        Returns the file's parsed JSON contents.
        """
        # For eatch uploaded file by user
        # has used encoding utf-8
        # to add support for other encodings
        # change encoding='utf-8' to codec selected by user
        with open(self.path, encoding='utf-8') as f:
            return json.load(f, **kwargs)

    def write(self, file):
        """
        Write another file's contents to this file.

        :param file: a ``django.core.files.File`` object
        """
        self._makedirs()
        with open(self.path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

    def write_json_to_zip(self, files, pretty_json=None, codec=None):
        """
        Writes JSON data to a ZIP file.

        :param files: a dict in which keys are file names and values are file contents, or a generator that yields
                      tuples of file names and file contents.
        """
        self._makedirs()
        kwargs = {}

        if pretty_json:
            kwargs['indent'] = 2

        if isinstance(files, dict):
            files = files.items()

        # It is necessary to modify
        # def json_dumps(data, ensure_ascii=False, **kwargs) in
        # https://github.com/open-contracting/ocdskit/blob/master/ocdskit/util.py
        # to add support for output encoding
        '''
        def json_dumps(data, ensure_ascii=False, codec="utf-8", **kwargs):
            """
            Dumps JSON to a string, and returns it.
            """
            # orjson doesn't support `ensure_ascii`, `indent` or `separators`.
            if not using_orjson or ensure_ascii or kwargs:
                if 'indent' not in kwargs:
                    kwargs['separators'] = (',', ':')
                result = json.dumps(data, default=_default, ensure_ascii=ensure_ascii, **kwargs)
                if not ensure_ascii and codec != "utf-8":
                    result = result.encode(codec)
                return result

            # orjson dumps to bytes.
            return orjson.dumps(data, default=_default).decode()
        '''
        # and change zipfile.writestr to zipfile.write
        # to write byte streams under encoding other than the used by default writestr method (utf-8)

        if codec:
            # thi is incorrect implementation
            # because json.dumps() in def json_dumps, use the default codec utf-8 to encode the output
            # so, codec selected with user --> codec utf-8 in def json_dumps
            tmpfiles = {}
            for name, content in files:
                data = json.dumps(content).encode(codec)
                tmpfiles.update({str(name): json.loads(data)})
            files = dict(tmpfiles)
            files = files.items()

        with ZipFile(self.path, 'w', compression=ZIP_DEFLATED) as zipfile:
            for name, content in files:
                # change to zipfile.write(....)
                zipfile.writestr(name, json_dumps(content, **kwargs) + '\n')

    @property
    def _name(self):
        """
        Returns the file's name.
        """
        return self.prefix + self.sep + self.id + self.ext

    @property
    def _directory(self):
        """
        Returns the directory containing the file.
        """
        return os.path.join(settings.MEDIA_ROOT, self.folder)

    def _makedirs(self):
        """
        Creates the directory to contain the file.
        """
        os.makedirs(self._directory, exist_ok=True)
