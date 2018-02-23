"""
This module contains functions which extract features from git log entries.
"""

import re
import numpy as np
import pandas as pd

from collections import defaultdict
from .gitcmds import get_git_log, get_bugfix_commits, link_fixes_to_bugs, \
    trim_hash


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
    feats: defaultdict
        A dictionary of feature values.
    """

    feats = defaultdict(lambda: None)
    lines = commit_str.splitlines()

    # parse the commit line
    commit_line = [line for line in lines if line.startswith('commit')][0]
    feats['hash'] = \
        trim_hash(re.match(r'commit (\w{40})', commit_line).group(1))

    # NOTE: skip string features for now because the one-hot encoding is a pain
    # parse the author line
    # author_line = [line for line in lines if line.startswith('Author:')][0]
    # author_matches = re.match(r'Author: (.+) <(.+)>', author_line)
    # feats['user'] = author_matches.group(1)
    # feats['email'] = author_matches.group(2)

    # parse the date line
    time_line = [line for line in lines if line.startswith('Date:')][0]
    timestamp = re.match(r'Date: (.*)', time_line).group(1)
    # TODO: fix the hardcoded timezone
    created_at = pd.to_datetime(timestamp, utc=True).tz_convert('US/Central')
    feats['dayofweek'] = created_at.dayofweek
    feats['hour'] = created_at.hour

    # parse the body lines
    body_lines = [line.lstrip() for line in lines if line.startswith('    ')]
    feats['len_message'] = len('\n'.join(body_lines))

    # NOTE: skip string features for now because the one-hot encoding is a pain
    # feats['tag'] = body_lines[0].split()[0].rstrip(':')

    # if this is a merge commit fill some fields with NaNs
    if any([line.startswith('Merge:') for line in lines]):
        # feats['tag'] = 'MERGE'
        feats['changed_files'] = np.NaN
        feats['additions'] = np.NaN
        feats['deletions'] = np.NaN

        return feats

    # parse the changes line
    changes_line = lines[-1]

    changed_regex = r' ([0-9]+) file[s]{0,1} changed'
    insert_regex = r'.* ([0-9]+) insertion[s]{0,1}'
    delete_regex = r'.* ([0-9]+) deletion[s]{0,1}'

    if re.match(changed_regex, changes_line):
        feats['changed_files'] = \
                int(re.match(changed_regex, changes_line).group(1))

    if re.match(insert_regex, changes_line):
        feats['additions'] = int(re.match(insert_regex, changes_line).group(1))

    if re.match(delete_regex, changes_line):
        feats['deletions'] = int(re.match(delete_regex, changes_line).group(1))

    return feats


def get_features(commit=None):
    """Get commit-level features.

    Parameters
    ----------
    commit : str, optional
        The hash of the commit to get features for. If not given this will
        return features for all commits.

    Returns
    -------
    features : pd.DataFrame of shape [n_commits, n_features]
        The features to use for modeling. The dataframe is indexed by commit
        hash.
    """

    logstr = get_git_log(commit)

    feats = pd.DataFrame([parse_commit(c) for c in split_commits(logstr)])

    feats = feats.set_index('hash').fillna(0)

    return feats


def get_labels(pattern=None):
    """Get a label for each commit indicating whether it introduced a bug.

    Returns
    -------
    labels : pd.Series of shape (n_commits,)
        The labels to use for modeling. The dataframe is indexed by commit
        hash.
    """

    feats = get_features()

    fix_commits = get_bugfix_commits(pattern)

    bug_commits = link_fixes_to_bugs(fix_commits)

    labels = feats.index.isin(bug_commits).astype(int)

    # convert to DataFrame so everything is the same type
    return pd.Series(data=labels, index=feats.index, name='label')
