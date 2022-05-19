# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from pyzbar import pyzbar

block_cipher = None
ICON = 'epjs.ico'

a = Analysis(
    ['EPJS.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.datas += [('epjs.ico', ICON, 'DATA')]

# Dynamic libraries not detected because they are loaded by ctypes
a.binaries += TOC([
    (Path(dep._name).name, dep._name, 'BINARY')
    for dep in pyzbar.EXTERNAL_DEPENDENCIES
])



pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EPajakScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon = ICON
)
