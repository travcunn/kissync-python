Kissync (SmartFile Client)
==========================
[![Build Status](https://travis-ci.org/travcunn/kissync-python.png?branch=master)](https://travis-ci.org/travcunn/kissync-python)

A cross platfom file synchronization application for SmartFile


Running Kissync
============
    $ git clone https://github.com/travcunn/kissync-python.git kissync
    $ cd kissync
    $ python main.py


Building a Windows installer
=====================
__Prerequisites:__

1. [Python 2.7](http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi)
2. [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.7.exe/download)
3. [NSIS 2.46](http://prdownloads.sourceforge.net/nsis/nsis-2.46-setup.exe?download)

__Build:__

In the console, run:

    $ installer_windows.cmd

Alternatively, you can open *installer_windows.cmd* from the Windows file explorer.

The installer will named "Kissync.exe" in the directory "installer_windows"


Resource Packaging
===============
PySide has a simple packing system that allows for embedding of all the program resources (such as images) into one file. Using a program by Shuge Lee, these resources are collected automatically. This process has been simplified and automated in the make file. For images to be collected, they should be placed in "ui/images".

__Prerequisites:__ 

* pyside-tools

On Ubuntu/Debian, this can be installed using the following command:

    $ sudo apt-get install pyside-tools

__Build:__

To build the resources automatically, run the following command in the console:

    $ make resources

__Using resources__:

Since building the resources with the make file puts a "resources.py" into the UI folder, any UI component that references external images will automatically discover the resources file, assuming it is in the same folder. 

To use any packaged resource in the UI, refer to the following example:
 
    QtGui.QIcon(":/menuicon.png")

This allows us to reference a resource with the file name ":/menuicon.png"

Links
====
[Official Kissync Website](http://www.kissync.com)

[MIT License](https://github.com/kissync/kissync-python/blob/master/LICENSE.MIT)

[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/83ebee1008a3caf7f74f8a98c5b44cea "githalytics.com")](http://githalytics.com/kissync/kissync-python)
