@echo off
set PYTHON="C:\Python27\python.exe"
set BUILDDIR="installer_windows"
set NSIS="C:\Program Files (x86)\NSIS\makensis.exe"
rmdir /s /q %BUILDDIR%/imageformats
rmdir /s /q build
rmdir /s /q dist
mkdir %BUILDDIR%
mkdir %BUILDDIR%/imageformats
rmdir /s /q build
%PYTHON% setup-build.py py2exe
copy ui\images\icon.ico %BUILDDIR%
copy dist\_ctypes.pyd %BUILDDIR%
copy dist\_hashlib.pyd %BUILDDIR%
copy dist\_multiprocessing.pyd %BUILDDIR%
copy dist\_socket.pyd %BUILDDIR%
copy dist\_ssl.pyd %BUILDDIR%
copy dist\API-MS-Win-Core-LocalRegistry-L1-1-0.dll %BUILDDIR%
copy dist\bz2.pyd %BUILDDIR%
copy dist\cacert.pem %BUILDDIR%
copy dist\Kissync.exe %BUILDDIR%
copy dist\library.zip %BUILDDIR%
copy dist\MPR.dll %BUILDDIR%
copy dist\pyexpat.pyd %BUILDDIR%
copy dist\PySide.QtCore.pyd %BUILDDIR%
copy dist\PySide.QtGui.pyd %BUILDDIR%
copy dist\PySide.QtNetwork.pyd %BUILDDIR%
copy dist\PySide.QtWebKit.pyd %BUILDDIR%
copy dist\pyside-python2.7.dll %BUILDDIR%
copy dist\python27.dll %BUILDDIR%
copy dist\pywintypes27.dll %BUILDDIR%
copy dist\QtCore4.dll %BUILDDIR%
copy dist\QtGui4.dll %BUILDDIR%
copy dist\QtNetwork4.dll %BUILDDIR%
copy dist\QtWebKit4.dll %BUILDDIR%
copy dist\select.pyd %BUILDDIR%
copy dist\shiboken-python2.7.dll %BUILDDIR%
copy dist\unicodedata.pyd %BUILDDIR%
copy dist\w9xpopen.exe %BUILDDIR%
copy dist\win32api.pyd %BUILDDIR%
copy dist\win32pipe.pyd %BUILDDIR%
copy dist\win32wnet.pyd %BUILDDIR%
copy dist\imageformats\qico4.dll %BUILDDIR%\imageformats
copy dist\imageformats\qjpeg4.dll %BUILDDIR%\imageformats
copy "C:\OpenSSL-Win32\libeay32.dll" %BUILDDIR%
copy "C:\OpenSSL-Win32\ssleay32.dll" %BUILDDIR%
copy builder\kissync.nsi %BUILDDIR%
pushd %BUILDDIR%
%NSIS% kissync.nsi
del Kissync.exe
del icon.ico
del _ctypes.pyd
del _hashlib.pyd
del _multiprocessing.pyd
del _socket.pyd
del _ssl.pyd
del API-MS-Win-Core-LocalRegistry-L1-1-0.dll
del bz2.pyd
del cacert.pem
del library.zip
del MPR.dll
del pyexpat.pyd
del PySide.QtCore.pyd
del PySide.QtGui.pyd
del PySide.QtNetwork.pyd
del PySide.QtWebKit.pyd
del pyside-python2.7.dll
del python27.dll
del pywintypes27.dll
del QtCore4.dll
del QtGui4.dll
del QtNetwork4.dll
del QtWebKit4.dll
del select.pyd
del shiboken-python2.7.dll
del unicodedata.pyd
del w9xpopen.exe
del win32api.pyd
del win32pipe.pyd
del win32wnet.pyd
del imageformats\qico4.dll
del imageformats\qjpeg4.dll
del libeay32.dll
del ssleay32.dll
rmdir /s /q imageformats
del kissync.nsi
popd
pushd ../%BUILDDIR%
rmdir /s /q dist
rmdir /s /q build
pause
