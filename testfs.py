import fs.base
from fs.osfs import OSFS


sync_fs = OSFS('C:\Users\Travis\Kissync')

for path in sync_fs.walkfiles():
    print path
    systemPath = sync_fs.getsyspath(path).strip("\\\\?\\")
    print systemPath
