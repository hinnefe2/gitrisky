"""This module contains cli commands to train and score gitrisky models"""

import click


@click.group
def cli():
    pass


@cli.command()
def train():
    """Train a git commit bug risk model"""
    pass


@cli.command()
def predict():
    """Score a git commit bug risk model"""
    pass
