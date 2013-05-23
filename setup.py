#!/bin/env python

from setuptools import setup

setup(
    name='main.py',
    version="1.0",
    description='Kissync Desktop Client',
    install_requires=[
        'PyYAML',
        'argparse',
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
        'watchdog',
        'wsgiref'
    ],
    author='Travis Cunningham and Taylor Brazelton',
    author_email='travcunn@umail.iu.edu',
    license='GPLv2',
)
