from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['os', 'asyncio', 'pkg_resources._vendor', 'numpy', 'idna'], excludes = ['tkinter'])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('WxPathfinder.py', base=base, targetName = 'Pathfinder.exe', icon='resources/PF.ico')
]

setup(name='Pathfinder',
      version = '2.0',
      description = 'Pathfinder',
      options = dict(build_exe = buildOptions),
      executables = executables)
