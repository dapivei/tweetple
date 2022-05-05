#!/usr/bin/env python3
# encoding: utf-8
# ============================================================================
"""Setup Package"""

import os

from setuptools import setup


def read_file(filename):
    """Read file
    ...
    """
    with open(os.path.join(os.getcwd(), filename), encoding='UTF-8') as f:
        return f.read()


setup(
    name='tweetple',
    version='0.92',
    author='Daniela Pinto Veizaga',
    author_email='danielapintoveizaga@gmail.com',
    description='A python wrapper for users of the Academic Research product track.',
    packages=['tweetple'],
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[
        'certifi==2021.10.8',
        'charset-normalizer==2.0.7',
        'cramjam==2.5.0',
        'decorator==5.1.0',
        'fsspec==2021.11.0',
        'idna==3.3',
        'numpy==1.21.4',
        'pandas==1.3.4',
        'pyarrow==6.0.1',
        'python-dateutil==2.8.2',
        'pytz==2021.3',
        'requests==2.26.0',
        'setuptools==58.3.0',
        'six==1.16.0',
        'thrift==0.15.0',
        'tqdm==4.62.3',
        'urllib3==1.26.7',
        'validators==0.18.2',
        'wheel==0.37.0'
    ],
    url='https://github.com/dapivei/tweetple',
    zip_safe=False
)
