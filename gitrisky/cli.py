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
def train():
    """Train a git commit bug risk model.

    This will save a pickled sklearn model to a file in the toplevel directory
    for this repository.
    """

    # get the features and labels by parsing the git logs
    features = get_features()

    # we can't train a model without positive training examples so we fail with
    # an informative error message
    try:
        labels = get_labels()
    except ValueError:
        # TODO: update this message once we support more / custom bug tags
        print('Failed to find any bug commits by parsing commit logs.\n'
              'gitrisky looks for commit messages containing "bug" or "fix" '
              'and this repo appears not to have any.')
        sys.exit(1)

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
