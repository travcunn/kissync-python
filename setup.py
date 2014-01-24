#!/bin/env python

from distutils.core import setup

setup(
    name='main.py',
    version="1.0",
    description='SmartFile Desktop Client',
    install_requires=[
        'coverage',
        'coveralls',
        'oauthlib',
        'pathtools',
        'python-dateutil',
        'python-librsync',
        'requests',
        'requests-oauthlib',
        'smartfile',
        'tendo',
        'watchdog',
        'wsgiref'
    ],
    author='Travis Cunningham',
    author_email='travcunn@umail.iu.edu',
    license='MIT',
)
