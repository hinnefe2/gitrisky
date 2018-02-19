import mock
import pickle

from collections import namedtuple
from tempfile import NamedTemporaryFile
from gitrisky.model import _get_model_path, create_model, load_model, \
    save_model


@mock.patch('gitrisky.model.Repo')
def test_get_model_path(mock_Repo):

    # fake version of the Repo class
    Repo = namedtuple('Repo', 'working_tree_dir')
    fake_instance = Repo('path/to/repo')

    # make the mocked constructor return the fake instance
    mock_Repo.return_value = fake_instance

    path = _get_model_path()

    assert isinstance(path, str)
    assert path == 'path/to/repo/gitrisky.model'


def test_create_model():

    model = create_model()

    assert hasattr(model, 'fit')
    assert callable(getattr(model, 'fit'))

    assert hasattr(model, 'predict_proba')
    assert callable(getattr(model, 'predict_proba'))


@mock.patch('gitrisky.model._get_model_path')
def test_load_model(mock_gmp):

    with NamedTemporaryFile() as tmpfile:

        pickle.dump('fake model', tmpfile)
        tmpfile.seek(0)

        mock_gmp.return_value = tmpfile.name
        model = load_model()

    assert model == 'fake model'


@mock.patch('gitrisky.model._get_model_path')
def test_save_model(mock_gmp):

    with NamedTemporaryFile() as tmpfile:

        mock_gmp.return_value = tmpfile.name
        save_model('fake model')

        tmpfile.seek(0)
        model = pickle.load(tmpfile)

    assert model == 'fake model'
