# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['weather-cmd.py'],  # just pick ONE main script to satisfy Analysis
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['engineio.async_drivers.threading'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Console EXE
exe_console = EXE(
    pyz,
    [('weather-cmd', 'weather-cmd.py', 'PYTHON')],
    a.binaries,
    a.datas,
    [],
    name='WeatherPeg-console',
    console=True,
)

# Windowed EXE
exe_windowed = EXE(
    pyz,
    [('weather-cmd', 'weather-cmd.py', 'PYTHON')],
    a.binaries,
    a.datas,
    [],
    name='WeatherPeg-windowed',
    console=False,
)

# Widget EXE
exe_widget = EXE(
    pyz,
    [('weatherwidget', 'weatherwidget.py', 'PYTHON')],
    a.binaries,
    a.datas,
    [],
    name='WeatherPeg-widget',
    console=False,
)
