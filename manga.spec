# manga.spec
# -*- mode: python ; coding: utf-8 -*-
import certifi

block_cipher = None

a = Analysis(
    ['manga.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('.venv/lib/python3.12/site-packages/pyfiglet/fonts', 'pyfiglet/fonts'),
        ('.venv/lib/python3.12/site-packages/certifi/cacert.pem', 'certifi')  # Ensure the path is to the file
    ],
    hiddenimports=['util', '__init__', 'crawler', 'sql'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='manga',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='manga',
)