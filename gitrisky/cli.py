"""This module contains cli commands to train and score gitrisky models"""

import sys
import click

from .model import create_model, save_model, load_model
from .gitcmds import get_latest_commit
from .parsing import get_features, get_labels


@click.group()
def cli():
    pass


@cli.command()
@click.option('-p', '--pattern', required=False,
              help="Bug fix pattern. Ex. BUG,FIX", type=str)
def train(pattern=None):
    """Train a git commit bug risk model.

    This will save a pickled sklearn model to a file in the toplevel directory
    for this repository.
    """

    # get the features and labels by parsing the git logs
    features = get_features()
    if pattern is not None:
        labels = get_labels(pattern.split(','))
    else:
        labels = get_labels(pattern)

    # instantiate and train a model
    model = create_model()
    model.fit(features, labels)

    print('Model trained on {n} training examples with {n_bug} positive cases'
          .format(n=len(features), n_bug=sum(labels)))

    # pickle the model to a file in the top level repo directory
    save_model(model)


@cli.command()
@click.option('-c', '--commit', type=str)
def predict(commit):
    """Score a git commit bug risk model.

    Parameters
    ----------
    commit: str
        The hash of the commit to score.

    Raises
    ------
    NotFittedError
        If a gitrisky model has not yet been trained on the currrent repo.
    """

    try:
        model = load_model()
    except FileNotFoundError:
        print('could not find trained model. '
              'have you run "gitrisky train" yet?')
        sys.exit(1)

    if commit is None:
        commit = get_latest_commit()

    features = get_features(commit)

    # pull out just the postive class probability
    [(_, score)] = model.predict_proba(features)

    print('Commit {commit} has a bug score of {score} / 1.0'
          .format(commit=commit, score=score))
