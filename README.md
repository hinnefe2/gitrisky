# gitrisky
[![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg)](http://opensource.org/licenses/MIT)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/gitrisky.svg)](https://pypi.python.org/pypi/gitrisky/)
[![Build Status](https://travis-ci.com/hinnefe2/gitrisky.svg?branch=master)](https://travis-ci.com/hinnefe2/gitrisky)
[![codecov](https://codecov.io/gh/hinnefe2/gitrisky/branch/master/graph/badge.svg)](https://codecov.io/gh/hinnefe2/gitrisky)
![hasbadges](https://z2x6abi6e2.execute-api.us-east-1.amazonaws.com/v1/hasbadges?user=hinnefe2&repo=gitrisky)


Predict code bug risk with git metadata


## Installation
Installation with `pip` is recommended:
```
pip install gitrisky
```
Note that `gitrisky` requires `numpy`. If you don't already have it `pip` will
try to install it for you, but this can result in a suboptimal build, see e.g.
[here](https://github.com/scikit-learn/scikit-learn/issues/2569).

For development a few additional dependencies are required:
```
pip install -r requirements-dev.txt
```

## Usage
`gitrisky` is installed as a command line tool.
```
Usage: gitrisky [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  predict  Score a git commit bug risk model.
  train    Train a git commit bug risk model.
```
The typical workflow is to first train a model on the existing commit history
of a repository:
```
$ cd repo/
$ gitrisky train
Model trained on 69 training examples with 14 positive cases
```
and then use the trained model to score subsequent commits:
```
$ gitrisky predict
Commit 910cdb3c has a bug score of 0.2 / 1.0
```
When invoked without any extra arguments `gitrisky predict` will score the most
recent commit. You can also score a particular commit with the `-c` flag:
```
$ gitrisky predict -c 470741f
Commit 470741f has a bug score of 0.7 / 1.0
```

## How does it work?
See this [PyData talk](https://www.youtube.com/watch?v=2yzWrI3zGY0) for an explanation of how `gitrisky` works.


## Contributing
Contributions are welcome! Please see `CONTRIBUTING.md` for information about
contributing to this project.


## License
The code in this project is licensed under the MIT license. See `LICENSE` for details.


## Acknowledgements
The initial prototype of `gitrisky` was developed at
[Civis Analytics](https://github.com/civisanalytics) during my 'Hack Time'
(time explicitly allotted to explore offbeat ideas) .
