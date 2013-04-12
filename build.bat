REM dist\client.exe --terminate

REM delete old directores
REM rmdir /s /q build
REM rmdir /s /q dist

c:\python27\python setup.py py2exe

pause