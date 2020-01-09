from default.data_file import DataFile


def test_repr_with_folder():
    data_file = DataFile('result', '.zip', id='identifier', folder='directory')

    assert repr(data_file) == 'directory/result-identifier.zip'


def test_repr_without_folder():
    data_file = DataFile('result', '.zip', id='identifier')

    assert repr(data_file) == '{:%Y-%m-%d}/result-identifier.zip'.format(date.today())
