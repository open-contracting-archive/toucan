import json
import os
import uuid
from datetime import date, datetime
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

    def __init__(self, prefix, ext, id=None, folder=None, timestamp=None, origin=None, url_suffix=None):
        if len(prefix) > 20:
            prefix = prefix[:20 + 1]

        self.prefix = prefix
        self.ext = ext
        self.id = id or str(uuid.uuid4())
        self.timestamp = timestamp or str(datetime.now())
        self.origin = origin
        self.url_suffix = url_suffix

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
        return os.path.join(self._directory, self.name)

    @property
    def url(self):
        """
        Returns the URL path to the file.
        """
        if self.url_suffix:
            return '/result/{}/{}/{}/'.format(self.folder, self.id, self.url_suffix)
        return '/result/{}/{}/'.format(self.folder, self.id)

    @property
    def drive_url(self):
        """
        Returns the URL path to the Google Drive save feature for the file.
        """
        return '/google-drive-save-start/{}/{}/'.format(self.folder, self.id)

    @property
    def size(self):
        """
        Returns the size of the file.
        """
        return os.path.getsize(self.path)

    def json(self, codec='utf-8', **kwargs):
        """
        Returns the file's parsed JSON contents.
        """
        with open(self.path, encoding=codec) as f:
            return json.load(f, **kwargs)

    def write(self, content):
        """
        Write another file's contents to this file.

        :param content: either a ``django.core.files.File`` object or a bytes array
        """
        self._makedirs()
        with open(self.path, 'wb') as f:
            if getattr(content, 'chunks', None):
                for chunk in content.chunks():
                    f.write(chunk)
            else:
                f.write(content)

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

        with ZipFile(self.path, 'w', compression=ZIP_DEFLATED) as zipfile:
            for name, content in files:
                zipfile.writestr(name, (json_dumps(content, **kwargs) + '\n').encode(codec))

    @property
    def name(self):
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
