# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_all

block_cipher = None

# Collect Panda3D data files
datas = collect_data_files('panda3d')
datas += collect_all('direct')[0]
datas += collect_all('panda3d')[0]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'panda3d',
        'panda3d.core',
        'panda3d.direct',
        'direct',
        'direct.showbase',
        'direct.showbase.ShowBase',
        'direct.task',
        'direct.task.Task',
        'direct.gui',
        'direct.gui.OnscreenText',
        'direct.gui.OnscreenText.OnscreenText',
        'direct.showbase.DirectObject',
        'direct.filter',
        'direct.filter.FilterManager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IronWings',
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
    icon='icon.ico'
)
