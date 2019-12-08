import mock

from click.testing import CliRunner
from gitrisky.cli import cli


@mock.patch('gitrisky.cli.get_features')
@mock.patch('gitrisky.cli.get_labels')
@mock.patch('gitrisky.cli.create_model')
@mock.patch('gitrisky.cli.save_model')
def test_cli_train(m_save_model, m_create_model, m_get_labels, m_get_features):

    # make some fake features and labels
    m_get_features.return_value = [[1, 1], [2, 2]]
    m_get_labels.return_value = [0, 1]

    # test the 'gitrisky train' cli command
    runner = CliRunner()
    result = runner.invoke(cli, ['train'])

    assert result.exit_code == 0
    assert result.output == \
        'Model trained on 2 training examples with 1 positive cases\n'

    for mck in [m_save_model, m_create_model, m_get_labels, m_get_features]:
        assert mck.call_count == 1


@mock.patch('gitrisky.cli.get_features')
@mock.patch('gitrisky.cli.get_labels')
@mock.patch('gitrisky.cli.create_model')
@mock.patch('gitrisky.cli.save_model')
def test_cli_train_no_bugs(m_save_model, m_create_model, m_get_labels,
                           m_get_features):

    # make some fake features and labels
    m_get_features.return_value = [[1, 1], [2, 2]]
    m_get_labels.side_effect = ValueError('No bug commits found')

    # test the 'gitrisky train' cli command
    runner = CliRunner()
    result = runner.invoke(cli, ['train'])

    assert result.exit_code == 1
    assert result.output == (
        'Failed to find any bug commits by parsing commit logs.\n'
        'gitrisky looks for commit messages containing "bug" or "fix" '
        'and this repo appears not to have any.\n')


@mock.patch('gitrisky.cli.get_features')
@mock.patch('gitrisky.cli.get_latest_commit')
@mock.patch('gitrisky.cli.load_model')
def test_cli_predict(m_load_model, m_get_latest_commit, m_get_features):

    runner = CliRunner()

    model = mock.MagicMock()
    model.predict_proba.return_value = [(0.1, 0.9)]

    m_load_model.return_value = model
    m_get_latest_commit.return_value = 'abcd'

    # test what happens when we don't specify a commit
    result = runner.invoke(cli, ['predict'])

    assert m_get_features.called_with('abcd')
    assert result.output == 'Commit abcd has a bug score of 0.9 / 1.0\n'
    assert result.exit_code == 0

    # test what happens when we specify a commit
    result = runner.invoke(cli, ['predict', '-c', '12345'])

    assert m_get_features.called_with('12345')
    assert result.output == 'Commit 12345 has a bug score of 0.9 / 1.0\n'
    assert result.exit_code == 0

    # test what happens when we can't load the model
    m_load_model.side_effect = FileNotFoundError()

    result = runner.invoke(cli, ['predict'])

    assert result.output == \
        'could not find trained model. have you run "gitrisky train" yet?\n'
    assert result.exit_code == 1
