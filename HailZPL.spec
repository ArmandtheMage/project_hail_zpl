# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\lucariellorm\\OneDrive - Gewiss S.p.A\\Desktop\\Project Hail ZPL\\run.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\lucariellorm\\OneDrive - Gewiss S.p.A\\Desktop\\Project Hail ZPL\\azure_project', 'azure_project'), ('C:\\Users\\lucariellorm\\OneDrive - Gewiss S.p.A\\Desktop\\Project Hail ZPL\\export', 'export'), ('C:\\Users\\lucariellorm\\OneDrive - Gewiss S.p.A\\Desktop\\Project Hail ZPL\\gui', 'gui')],
    hiddenimports=['azure_project.azure_handler', 'azure_project.query_handler', 'export.excel_handler', 'gui.gui'],
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
    a.binaries,
    a.datas,
    [],
    name='HailZPL',
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
)
