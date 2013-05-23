Kissync (SmartFile Client)
==========================
[![Build Status](https://travis-ci.org/kissync/kissync-python.png?branch=master)](https://travis-ci.org/kissync/kissync-python)
#####*Currently builds specifically for Ubuntu 10 and newer, but can port to other systems

A file synchronization and browsing tool for SmartFile in Python


Running Kissync
===================


    $ git clone https://github.com/kissync/kissync-python.git kissync
    $ cd kissync
    $ python main.py


Using Kissync
===============

The Kissync client is used to view your files on the Smartfile servers. All file access is done over SSL. 

####Bottom Bar ( Delete, move, rename, etc... )
Single click on your file. The panel at the bottom should appear. From there just select the operation you wish to occur and then follow the on screen instructions.

If you generated a link to the file to share, then the URL should be automatically placed onto your clipboard so you can just Right Click and select Paste where you need to place the link.

These operations happen via a task manager provided online by the SmartFile team. Please allow up to 2 minutes for your changes to take effect. 

####Bread Crumbs
The breadcrumbs are an essential part to the SmartFile client. It allows for the users to navigate back through the folders until they reach their root directory.

####Logging Out
If you are in need of logging out. You can accomplish this task by pressing the Logout button at the top right of the page, it should be right underneath your full name.

####Local Files
Taking a look at your home directory you might see a new folder after you've run the Kissync app for the first time. The folders name should be "Kissync" and it might contain just a few of the files from the server. If it doesn't contain anything however do not be concerned. You can start placing anything from your local file system directly into this folder and automatically it should be synced with the server. ( Give up to 2 to 5 minutes to sync, this really depends upon the files size. )

Links
=============

[Kissync](http://kissync.com)

[GPL License](https://github.com/kissync/kissync-python/blob/master/LICENSE.GPL)

[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/83ebee1008a3caf7f74f8a98c5b44cea "githalytics.com")](http://githalytics.com/kissync/kissync-python)
