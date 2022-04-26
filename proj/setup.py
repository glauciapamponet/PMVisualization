from cx_Freeze import setup, Executable
import sys

base = None

if sys.platform == 'win64':
    base = None


executables = [Executable("run.py", base=base)]

packages = ["igraph", "plotly", "flask", "pandas", "flask_wtf", "pywebview"]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = "IC",
    options = options,
    version = "1.0",
    description = 'Process Mining View',
    executables = executables
)