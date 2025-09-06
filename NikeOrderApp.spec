# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['launcher.py'],   # entry script
    pathex=[],
    binaries=[],
    datas=[
        ('data/*', 'data'),
        ('filtered_summary.xlsx', '.'),
        ('filtered_summary.csv', '.'),
        ('bfg.jar', '.'),
        ('index.html', '.'),
        ('app.py', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['inspect'],   # 👈 exclude inspect to avoid MemoryError
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NikeOrderApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)

# 👇 Onedir build (not onefile) to avoid memory issues
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NikeOrderApp'
)
