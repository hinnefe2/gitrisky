"""This module contains cli commands to train and score gitrisky models"""

import click

from sklearn.ensemble import RandomForestClassifier

from .model import save_model, load_model
from .gitcmds import get_latest_commit
from .parsing import get_features, get_labels


@click.group
def cli():
    pass


@cli.command()
def train():
    """Train a git commit bug risk model.

    This will save a pickled sklearn model to a file in the toplevel directory
    for this repository.
    """

    # get the features and labels by parsing the git logs
    features = get_features()
    labels = get_labels()

    # instantiate and train a model
    model = RandomForestClassifier()
    model.train(features, labels)

    print('Trained a model on {n} training examples with {n_bug} positive cases'
          .format(n=len(features), n_bug=sum(labels)))

    # pickle the model to a file in the top level repo directory
    save_model(model)


@cli.command()
@click.option('-c', '--commit', type=str)
def predict(commit):
    """Score a git commit bug risk model

    Parameters
    ----------
    commit: str
        The hash of the commit to score.

    Raises
    ------
    NotFittedError
        If a gitrisky model has not yet been trained on the currrent repo.
    """

    model = load_model()

    if commit is None:
        commit = get_latest_commit()

    features = get_features(commit)

    score = model.predict_proba(features)

    print('Commit {commit} has a bug score of {score} / 1.0'
          .format(commit=commit, score=score))
