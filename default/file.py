import os
import uuid
from datetime import date

from django.conf import settings


def save_file(uploadedfile):
    name, ext = uploadedfile.name.rsplit('.', 1)
    name_handler = FilenameHandler(name, '.' + ext)
    file_path = name_handler.generate_full_path()
    with open(file_path, 'wb') as newfile:
        for chunk in uploadedfile.chunks():
            newfile.write(chunk)
    return name_handler.as_dict()


class FilenameHandler:
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

    def as_dict(self):
        return self.__dict__

    @property
    def name(self):
        """
        Returns the file name.
        """
        return self.prefix + self.sep + self.id + self.ext

    def name_with_suffix(self, suffix):
        """
        Returns the file name, with a suffix before its extension.
        """
        return self.prefix + self.sep + self.id + suffix + self.ext

    @property
    def directory(self):
        """
        Returns the directory containing the file.
        """
        return os.path.join(settings.MEDIA_ROOT, self.folder)

    @property
    def path(self):
        """
        Returns the full path to the file.
        """
        return os.path.join(self.directory, self.name)

    def generate_full_path(self):
        """
        Returns the full path to the file, creating its containing directory if non-existent.
        """
        os.makedirs(self.directory, exist_ok=True)
        return self.path
