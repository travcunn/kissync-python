#!/bin/env python

import os
import sys
from distutils.core import setup

if sys.platform == 'darwin':
    import py2app
elif sys.platform == 'win32':
    import py2exe
else:
    #print "Unknown platform: %s" % sys.platform
    sys.exit(-1)

setup(
    name='kissync.py',
    version="1.0",
    description='Kissync Desktop Client',
    author='Kissync',
    author_email='travcunn@umail.iu.edu',
    options={
        "py2exe": {
            "unbuffered": True,
            "optimize": 2,
            "bundle_files": 1,
            "dll_excludes": ["libeay32.dll", "w9xpopen.exe", "MSVCP90.dll"],
            "includes": ["sip", "PyQt4.QtNetwork."]
        },

        "py2app": {
            "optimize": 2,
            "argv_emulation": True,
            "plist": {'LSBackgroundOnly': True},
        }
    },
    data_files=[('', ['cacert.pem'])],
    requires=[
        'smartfile',
        'oauthlib',
        'requests',
        'requests_oauthlib',
        'pathtools',
        'watchdog',
    ],
    app=["kissync.py"],

    zipfile=None,
    console=[{
        "script": "kissync.py",
    }]
)
