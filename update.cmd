py -3.7-64 -m twine check dist/*
if errorlevel 1 goto :eof
py -3.7-64 -m twine upload dist/*
