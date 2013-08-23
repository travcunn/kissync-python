import fs.base
from fs.osfs import OSFS


sync_fs = OSFS('/home/travis/Kissync')

for object in sync_fs.walkfiles():
    print object
    print sync_fs.getsyspath(object)
