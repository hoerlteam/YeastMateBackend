# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import get_package_paths
import sys

sys.modules["FixTk"] = None

block_cipher = None


a = Analysis(['annotation.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['hooks'],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[
               "FixTk",
               "tcl",
               "tk",
               "_tkinter",
               "tkinter",
               "Tkinter",
               "matplotlib",
            ],
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
          name='annotation',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='annotation')