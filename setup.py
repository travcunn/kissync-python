#!/bin/env python

import os
import sys
from distutils.core import setup

setup(
		name = 'kissync.py',
    version = "1.0",
    description = 'Kissync Desktop Client',
    requires= [
				'smartfile',
				'oauthlib',
        'requests',
        'requests_oauthlib',
        'pathtools',
        'watchdog',
    ],    
		author = 'Kissync',
    author_email='travcunn@umail.iu.edu',
    license='GPLv2',
)
