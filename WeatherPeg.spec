# weatherpeg_combined.spec
# Single spec file to build both console and console-less executables

block_cipher = None

a = Analysis(
    ['weather-cmd.py'],  # replace with your WeatherPeg entrypoint
    pathex=[],
    binaries=[],
    datas=[
        ('templates/*', 'templates'),  # include Flask templates
        ('static/*', 'static'),        # include Flask static files
    ],
    hiddenimports=['engineio.async_drivers.threading'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Console build
exe_console = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WeatherPeg_console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # Console version
)

# Console-less build
exe_noconsole = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WeatherPeg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Console-less version
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
