sc stop dufile
sc delete dufile
TIMEOUT /T 3
rmdir /s/q dist
rmdir /s/q build
del PythonService.spec
pyinstaller PythonService.py
dist\PythonService\PythonService.exe install
sc start dufile