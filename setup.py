from setuptools import setup, find_packages

VERSION = '0.1.3'


setup(

    name='gitrisky',

    description='Predict code bug risk with git metadata',

    version=VERSION,

    url='https://github.com/hinnefe2/gitrisky',

    download_url=('https://github.com/hinnefe2/gitrisky/archive/{}.tar.gz'
                  .format(VERSION)),

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

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        ],

    include_package_data=True,

    entry_points={
        'console_scripts': ['gitrisky=gitrisky.cli:cli'],
    },
)
