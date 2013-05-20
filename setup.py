#!/bin/env python

from distutils.core import setup

setup(
    name='kissync.py',
    version="1.0",
    description='Kissync Desktop Client',
    requires=[
        'PyYAML',
        'argparse',
        'beautifulsoup4',
        'coverage',
        'coveralls',
        'docopt',
        'oauthlib',
        'pathtools',
        'python-librsync',
        'requests',
        'requests-oauthlib',
        'sh',
        'smartfile',
        'tendo',
        'watchdog'
        'wsgiref'
    ],
    author='Kissync',
    author_email='travcunn@umail.iu.edu',
    license='GPLv2',
)
