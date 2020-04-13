setlocal
if not  "%1" == "" (
    set PY_VER=%1
) else (
    echo Error: %%1 must be python version: e.g. 3.7 3.6-32
    goto :eof
)

for %%i in (dist\*.whl) do set WHEEL=%%~fi
set PYTHONPATH=
cd %userprofile%
py -%PY_VER% -m pip install -U %WHEEL%

endlocal
