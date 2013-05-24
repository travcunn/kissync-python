# -*- mode: python -*-
a = Analysis(['main.py'], hiddenimports=[], hookspath=None)
a.datas.append(('cacert.pem', 'cacert.pem', 'DATA'))
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'main'),
          debug=False,
          strip=None,
          upx=True,
          console=False )