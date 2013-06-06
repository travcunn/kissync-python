#!/bin/env python

from distutils.core import setup
import py2exe, sys, os

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
    data_files=data_files,
    options={
        "py2exe":{
            "dll_excludes":['MSVCP90.dll'],
            'includes': ['PySide.QtNetwork'],
        }},
    windows = [{'script': "main.py"}],
)
