def get_files(session):
  for _file in session['files']:
    yield _file['info'], _file['size']

def has_files(session):
  return 'files' in session

def save_in_session(session, info_dict, size):
  if not 'files' in session:
    session['files'] = []
  session['files'].append({'info': info_dict, 'size': size})
  session.modified = True
