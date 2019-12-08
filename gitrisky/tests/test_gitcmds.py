import mock
import pytest

import numpy as np

from collections import defaultdict

from gitrisky.gitcmds import _run_bash_command, trim_hash, get_latest_commit, \
    get_git_log, get_bugfix_commits, _get_commit_filenames, \
    _get_commit_lines, _get_blame_commit, link_fixes_to_bugs


@mock.patch('gitrisky.gitcmds.check_output')
def test_run_bash_command(mock_co):

    cmd = 'some bash command'
    output = 'output from some command\n'.encode('utf-8')

    mock_co.return_value = output

    stdout = _run_bash_command(cmd)

    assert mock_co.called_with('some', 'bash', 'command')
    assert stdout == 'output from some command'


def test_trim_hash():

    long_hash = '123456789abcdefg'

    assert trim_hash(long_hash) == long_hash[:8]


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_latest_commit(mock_runbc):

    stdout = '4db4fc24afe7565ac65fdb272c7c157c43aace77'

    mock_runbc.return_value = stdout

    commit = get_latest_commit()

    assert isinstance(commit, str)
    assert len(commit) == 8
    assert commit == stdout[:8]
    assert mock_runbc.called_with('git log -1 --pretty=format:"%H"')


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_git_log(mock_runbc):

    stdout = ("Merge: 910cdb3 bbb59ea\n"
              "Author: Henry Hinnefeld <henry.hinnefeld@gmail.com>\n"
              "Date:   Sun Feb 4 15:55:45 2018 -0600\n"
              "\n"
              "    Merge pull request #10 from hinnefe2/write_readme\n"
              "\n"
              "    Write readme")

    mock_runbc.return_value = stdout

    # test calling with a commit specified
    log = get_git_log('1234abcd')

    assert mock_runbc.called_with('git --no-pager log --stat -1 1234abcd')
    assert log == stdout

    # test calling with no commit specified
    log = get_git_log()

    assert mock_runbc.called_with('git --no-pager log --stat')
    assert log == stdout


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_bugfix_commits(mock_runbc):

    stdout = "671e13d\n4fe1c42\n3e10227\n91d54e3\n2c3dca4"

    mock_runbc.return_value = stdout

    commits = get_bugfix_commits()

    assert mock_runbc.called_with(
        'git log -i --all --grep BUG --grep FIX --pretty=format:%h')
    assert np.array_equal(commits, ['671e13d', '4fe1c42', '3e10227',
                                    '91d54e3', '2c3dca4'])


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_bugfix_commits_no_bugs(mock_runbc):

    stdout = "\n"

    mock_runbc.return_value = stdout

    with pytest.raises(ValueError):
        get_bugfix_commits()


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_commit_filenames(mock_runbc):

    stdout = "gitrisky/cli.py\ngitrisky/model.py"

    mock_runbc.return_value = stdout

    fnames = _get_commit_filenames('dc95b21')

    # try when _get_commit_filenames returns multiple filenames
    assert isinstance(fnames, list)
    assert mock_runbc.called_with(
        'git --no-pager diff dc95b21 dc95b21^ --name-only')
    assert np.array_equal(fnames, ['gitrisky/cli.py', 'gitrisky/model.py'])

    # try when _get_commit_filenames returns single filename
    stdout = "gitrisky/cli.py"
    mock_runbc.return_value = stdout

    fnames = _get_commit_filenames('dc95b21')

    assert isinstance(fnames, list)


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_commit_lines(mock_runbc):

    # specify different return values for repeated calls to mock_runbc
    # note that this isn't the complete output of the relevant git command,
    # just the important bits
    stdout1 = ("@@ -5,3 +5 @@ import click\n"
               "@@ -30 +28 @@ def train():")
    stdout2 = ("@@ -6,0 +7 @@ from git import Repo\n"
               "@@ -26,0 +28,16 @@ def _get_model_path():")

    mock_runbc.side_effect = [stdout1, stdout2]

    lines = \
        _get_commit_lines('dc95b21', ['gitrisky/cli.py', 'gitrisky/model.py'])

    assert mock_runbc.called_with(
            'git --no-pager diff dc95b21^ dc95b21 -U0 -- gitrisky/cli.py')
    assert mock_runbc.called_with(
            'git --no-pager diff dc95b21^ dc95b21 -U0 -- gitrisky/model.py')

    assert isinstance(lines, defaultdict)

    # we deleted 3 lines after line 5 and 1 line after line 30 in cli.py
    assert np.array_equal(lines['gitrisky/cli.py'], [('5', '3'), ('30', '1')])

    # we didn't delete any lines in model.py
    assert np.array_equal(lines['gitrisky/model.py'], [])


@mock.patch('gitrisky.gitcmds._run_bash_command')
def test_get_blame_commit(mock_runbc):

    stdout1 = ("c668b98e (Henry Hinnefeld 2018-01-22 07:33:22 -0600 30)     model = RandomForestClassifier()")  # noqa
    stdout2 = ("c668b98e gitrisky/cli.py (Henry Hinnefeld 2018-01-22 07:33:22 -0600 5) from sklearn.ensemble import RandomForestClassifier\n"  # noqa
               "2f0b9d3b cli.py          (Henry Hinnefeld 2018-01-21 20:03:36 -0600 6) \n"  # noqa
               "209879e0 gitrisky/cli.py (Henry Hinnefeld 2018-01-22 07:34:16 -0600 7) from .model import save_model, load_model")  # noqa
    mock_runbc.side_effect = [stdout1, stdout2]

    filenames = ['gitrisky/cli.py', 'gitrisky/model.py']
    fname_lines = {'gitrisky/cli.py': [('5', '3'), ('30', '1')],
                   'gitrisky/model.py': []}

    bug_commits = _get_blame_commit('dc95b21', filenames, fname_lines)

    # check we called the right git commands
    assert mock_runbc.called_with(
        'git --no-pager blame -L5,+3 dc95b21^ -- gitrisky/cli.py')
    assert mock_runbc.called_with(
        'git --no-pager blame -L30,+1 dc95b21^ -- gitrisky/cli.py')

    assert isinstance(bug_commits, set)
    assert bug_commits == set(['c668b98e', '2f0b9d3b', '209879e0'])


def test_link_fixes_to_bugs():

    # NOTE: this is effectively an integration test because the
    # link_fixes_to_bugs function just chains all the other functions

    # NOTE: this test actually runs against the gitrisky repo history

    fix_commits = ['3e10227', '2c3dca4']

    bug_commits = link_fixes_to_bugs(fix_commits)

    assert isinstance(bug_commits, list)
    assert set(bug_commits) == set(['d90875b0', 'e359f619', 'bb47087b'])
