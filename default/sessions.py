from collections import OrderedDict
from .file import FilenameHandler

def get_files_contents(session):
    """ Generator that returns file contents from session info. """
    for fileinfo in session['files']:
        file_handler = FilenameHandler(**fileinfo)
        filename = file_handler.get_full_path()
        with open(filename, 'r', encoding='utf-8') as f:
            buf = f.read()
        yield file_handler, buf

def save_in_session(session, info):
  if not 'files' in session:
    session['files'] = []
  session['files'].append(info)
  session.modified = True
