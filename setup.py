"""
Dtella - py2exe setup script
Copyright (C) 2007-2008  Dtella Labs (http://dtella.org/)
Copyright (C) 2007-2008  Paul Marks (http://pmarks.net/)
Copyright (C) 2007-2008  Jacob Feisley (http://feisley.com/)

$Id: setup.py 559 2009-02-02 05:29:10Z sparkmaul $

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from distutils.core import setup
import sys

if sys.platform == 'darwin':
    import py2app
elif sys.platform == 'win32':
    import py2exe
else:
    print "Unknown platform: %s" % sys.platform
    sys.exit(-1)

setup(
    name = 'kissync.py',
    version = "1.0",
    description = 'Kissync Desktop Client',
    author = 'Kissync Team',
    options = {
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
            "plist": {'LSBackgroundOnly':True},
        }
    },
    data_files=[('', ['cacert.pem'])],
    app = ["kissync.py"],

    zipfile = None,
    console = [{
        "script": "kissync.py",
    }]
)
