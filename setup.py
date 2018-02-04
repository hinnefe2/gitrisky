from setuptools import setup, find_packages

VERSION = '0.1.0c'


setup(

    name='gitrisky',

    description='Predict code bug risk with git metadata',

    version=VERSION,

    url='https://github.com/hinnefe2/gitrisky',

    download_url='https://github.com/hinnefe2/gitrisky/archive/{}.tar.gz'.format(VERSION),

    author='J. Henry Hinnefeld',

    author_email='henry.hinnefeld@gmail.com',

    packages=find_packages(),

    install_requires=[
        'click>=6.7',
        'GitPython>=2.1',
        'numpy>=1.13',
        'pandas>=0.20',
        'scikit-learn>=0.19',
        'scipy>=0.19',
        ],


    include_package_data=True,

    entry_points={
        'console_scripts': ['gitrisky=gitrisky.cli:cli'],
    },
)
