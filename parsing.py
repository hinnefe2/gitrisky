"""
This module contains functions which extract features from git log entries.
"""

import re
import numpy as np
import pandas as pd

from collections import defaultdict


def split_commits(whole_log):
    """Split the output of git log into separate entries per commit.

    Parameters
    ----------
    whole_log: str
        A string containing the entire git log.

    Returns
    -------
    list(str)
        A list of log entries, with each commit as its own string.
    """

    lines = whole_log.splitlines()

    # find the indices which separate each commit's entry
    commit_line_idxs = [i for i, line in enumerate(lines)
                        if re.match(r'^commit \w{40}$', line)]

    # split the lines from the whole log into subsets for each log entry
    commit_lines = np.array_split(lines, commit_line_idxs)

    return ["\n".join(arr) for arr in commit_lines[1:]]


def parse_commit(commit_str):
    """Extract features from the text of a commit log entry.

    Parameters
    ----------
    commit_str: str
        The text of a commit log entry.

    Returns
    -------
    data: defaultdict
        A dictionary of feature values.
    """

    data = defaultdict(lambda: None)
    lines = commit_str.splitlines()

    # parse the commit line
    commit_line = [line for line in lines if line.startswith('commit')][0]
    data['hash'] = re.match(r'commit (\w{40})', commit_line).group(1)

    # parse the author line
    author_line = [line for line in lines if line.startswith('Author:')][0]
    author_matches = re.match(r'Author: (.+) <(.+)>', author_line)
    data['user'] = author_matches.group(1)
    data['email'] = author_matches.group(2)

    # parse the date line
    time_line = [line for line in lines if line.startswith('Date:')][0]
    timestamp = re.match(r'Date: (.*)', time_line).group(1)
    # TODO: fix the hardcoded timezone
    data['created_at'] = \
        pd.to_datetime(timestamp, utc=True).tz_convert('US/Central')

    # parse the body lines
    body_lines = [line.lstrip() for line in lines if line.startswith('    ')]
    data['message'] = '\n'.join(body_lines)
    data['tag'] = body_lines[0].split()[0].rstrip(':')

    # if this is a merge commit fill some fields with NaNs
    if any([line.startswith('Merge:') for line in lines]):
        data['tag'] = 'MERGE'
        data['changed_files'] = np.NaN
        data['additions'] = np.NaN
        data['deletions'] = np.NaN

        return data

    # parse the changes line
    changes_line = lines[-1]
    if re.match(r' ([0-9]+) file[s]{0,1} changed', changes_line):
        data['changed_files'] = int(re.match(r' ([0-9]+) file[s]{0,1} changed',
                                             changes_line).group(1))

    if re.match(r'.* ([0-9]+) insertion[s]{0,1}', changes_line):
        data['additions'] = int(re.match(r'.* ([0-9]+) insertion[s]{0,1}',
                                         changes_line).group(1))

    if re.match(r'.* ([0-9]+) deletion[s]{0,1}', changes_line):
        data['deletions'] = int(re.match(r'.* ([0-9]+) deletion[s]{0,1}',
                                changes_line).group(1))

    return data


def make_commit_log_df(filename):

    with open(filename) as infile:
        logstr = infile.read()

    return pd.DataFrame([parse_commit(c) for c in split_commits(logstr)])
