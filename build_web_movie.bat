sc stop web_movie 
sc delete web_movie
TIMEOUT /T 3
rmdir /s/q dist
rmdir /s/q build
del PythonService.spec
pyinstaller -F --add-data "templates;templates" --add-data "static;static" PythonService.py
dist\PythonService.exe --startup delayed-auto install
sc start web_movie 