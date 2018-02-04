import os

from setuptools import setup, find_packages


THIS_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(THIS_DIR, 'requirements.txt')) as reqs:
    requirements = reqs.read().strip().split('\n')


setup(

    name='gitrisky',

    description='Predict code bug risk with git metadata',

    version='0.1.0',

    url='https://github.com/hinnefe2/gitrisky',

    author='J. Henry Hinnefeld',

    author_email='henry.hinnefeld@gmail.com',

    packages=find_packages(),

    install_requires=requirements,

    entry_points={
        'console_scripts': ['gitrisky=gitrisky.cli:cli'],
    },
)
