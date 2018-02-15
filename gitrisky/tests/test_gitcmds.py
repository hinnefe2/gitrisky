import mock
import numpy as np

from collections import defaultdict

from gitrisky.gitcmds import _run_bash_command, trim_hash, get_latest_commit, \
    get_git_log, get_bugfix_commits, _get_commit_filenames, _get_commit_lines


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

    stdout = """
Merge: 910cdb3 bbb59ea
Author: Henry Hinnefeld <henry.hinnefeld@gmail.com>
Date:   Sun Feb 4 15:55:45 2018 -0600

Merge pull request #10 from hinnefe2/write_readme

            Write readme"""

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
    stdouts = ["""
@@ -5,3 +5 @@ import click
@@ -30 +28 @@ def train():""", """
@@ -6,0 +7 @@ from git import Repo
@@ -26,0 +28,16 @@ def _get_model_path():"""]

    mock_runbc.side_effect = stdouts

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
