# -*- mode: python -*-
a = Analysis(['/home/travis/Dropbox/kissync/kissync-client/main.py'],
             pathex=['/home/travis'],
             hiddenimports=[],
             hookspath=None)
a.datas.append(('cacert.pem', 'cacert.pem', 'DATA'))
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'KissyncClient'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
