# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['nova.py'],
    pathex=[],
    binaries=[],
    datas=[('Images', 'Images'), ('Fonts', 'Fonts'), ('nir', 'nir'), ('C:\\Program Files\\Tesseract-OCR', 'Tesseract-OCR')],
    hiddenimports=['customtkinter', 'easyocr', 'pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'comtypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='nova',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Images\\GIFS\\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='nova',
)
