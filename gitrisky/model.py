"""This module contains code to load and save gitrisky models"""

import os
import pickle

from git import Repo
from sklearn.ensemble import RandomForestClassifier


def _get_model_path():
    """Get the full path of the gitrisky model.

    For now this is hardcoded to be '<repo toplevel>/gitrisky.model'.

    Returns
    -------
    path : str
        The full path to the gitrisky model
    """

    # use gitpython.Repo to find the repository's top level directory
    repo_dir = Repo('.', search_parent_directories=True).working_tree_dir
    model_path = os.path.join(repo_dir, 'gitrisky.model')

    return model_path


def create_model():
    """Create a new model.

    Returns
    -------
    model : scikit-learn model
        A saved scikit-learn model
    """

    # instantiate a new model
    # TODO: replace this with a gridsearchCV object for hyperparameter tuning
    model = RandomForestClassifier()

    return model


def load_model():
    """Load a model from a pickle file.

    Returns
    -------
    model : scikit-learn model
        A saved scikit-learn model

    Raises
    ------
    FileNotFoundError
        If the trained model pickle file can't be found
    """

    model_path = _get_model_path()

    with open(model_path, 'rb') as infile:
        model = pickle.load(infile)

    return model


def save_model(model):
    """Save a model to a pickle file.

    Parameters
    ----------
    model : scikit-learn model
        The scikit-learn model to save.
    """

    model_path = _get_model_path()

    with open(model_path, 'wb') as outfile:
        pickle.dump(model, outfile)
