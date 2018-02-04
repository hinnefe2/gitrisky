import os

from setuptools import setup, find_packages


THIS_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(THIS_DIR, 'requirements.txt')) as reqs:
    requirements = reqs.read().strip().split('\n')


setup(

    name='gitrisky',

    description='Predict code bug risk with git metadata',

    version='0.1.0a',

    url='https://github.com/hinnefe2/gitrisky',

    download_url='https://github.com/hinnefe2/gitrisky/archive/v0.1.0a.tar.gz',

    author='J. Henry Hinnefeld',

    author_email='henry.hinnefeld@gmail.com',

    packages=find_packages(),

    install_requires=requirements,

    include_package_data=True,

    entry_points={
        'console_scripts': ['gitrisky=gitrisky.cli:cli'],
    },
)
