#!/bin/env python

from distutils.core import setup
# noinspection PyPackageRequirements
import py2exe, sys, os

if sys.platform == 'darwin':
    # noinspection PyPackageRequirements
    import py2app
elif sys.platform == 'win32':
    # noinspection PyPackageRequirements
    import py2exe
    _PYSIDEDIR = r'C:\Python27\Lib\site-packages\PySide'
    data_files =[('imageformats',[os.path.join(_PYSIDEDIR,'plugins\imageformats\qico4.dll')]),
             ('imageformats',[os.path.join(_PYSIDEDIR,'plugins\imageformats\qjpeg4.dll')]),
              ('.',[os.path.join(_PYSIDEDIR,'shiboken-python2.7.dll'),
                os.path.join(_PYSIDEDIR,'QtCore4.dll'),
                os.path.join(_PYSIDEDIR,'QtGui4.dll'), 
                os.path.join(_PYSIDEDIR,'QtNetwork4.dll')]),
                'cacert.pem'
              ]

setup(
    name = 'Kissync',
    version = "1.0",
    description = 'Kissync',
    author = 'Travis Cunningham',
    author_email='travcunn@umail.iu.edu',
    url = 'http://www.kissync.com',
    license='MIT',
    install_requires=[
        'coverage',
        'coveralls',
        'oauthlib',
        'pathtools',
        'python-librsync',
        'requests',
        'requests-oauthlib',
        'smartfile',
        'tendo',
        'watchdog',
        'wsgiref'
    ],
    data_files=data_files,
    options={
        "py2exe":{
            'dll_excludes':['MSVCP90.dll'],
            'includes': ['PySide.QtNetwork'],
        }},
    windows = [{
                'script': 'main.py',
                'icon_resources': [(1, "ui/images/icon.ico")],
                }],
)

os.rename('dist/main.exe','dist/Kissync.exe') 