# -*- mode: python -*-

import cloudscraper
import os
cloudscraper_dir = os.path.dirname( cloudscraper.__file__ )

block_cipher = None


a = Analysis(['hydrus/hydrus_client.py'],
             pathex=['.'],
             binaries=[],
             datas=[
               ('hydrus/bin', 'bin'),
               ('hydrus/help', 'help'),
               ('hydrus/static', 'static'),
               ('dist/hydrus_server/hydrus_server', '.'),
               ('hydrus/license.txt', '.'),
               ('hydrus/README.md', '.'),
               ('hydrus/help my client will not boot.txt', '.'),
               ('hydrus/db', 'db'),
               (cloudscraper_dir, 'cloudscraper')
             ],
             hiddenimports=['hydrus/hydrus_server.py'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='hydrus_client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='hydrus_client')