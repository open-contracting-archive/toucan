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

    def __init__(self, prefix, ext,\
            id=str(uuid.uuid4()),\
            generation_date=date.today(),
            truncate_prefix_by=20,
            folder=None):
        self.prefix = self._truncate_prefix(prefix, truncate_prefix_by)
        self.ext = ext
        self.id = id 
        if folder is not None:
            self.folder = folder
        else:
            self.folder = '{:%Y-%m-%d}'.format(generation_date)
            
    def as_dict(self):
        return { \
                'id': self.id, \
                'prefix': self.prefix, \
                'folder': self.folder, \
                'ext': self.ext \
                }

    def get_id(self):
        return self.id

    def get_full_name(self):
        return self.prefix + FilenameHandler.sep + self.id + self.ext

    def get_full_path(self):
        filename = self.get_full_name()
        return os.path.join(settings.MEDIA_ROOT, self.folder, filename)

    def get_folder(self):
        return os.path.join(settings.MEDIA_ROOT, self.folder)

    def generate_full_path(self):
        path_folder = os.path.join( \
                          settings.MEDIA_ROOT, \
                          self.folder)
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
        return self.get_full_path()

    def _truncate_prefix(self, prefix, length):
        if len(prefix) <= length:
            return prefix
        return prefix[:length + 1]

    def name_only_with_suffix(self, suffix):
        "Adds a suffix to the file name."
        return self.prefix + FilenameHandler.sep + self.id + suffix + self.ext
