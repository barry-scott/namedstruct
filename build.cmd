rmdir /s /q build
rmdir /s /q dist
rmdir /s /q namedstruct.egg-info

py -3.5 setup.py sdist bdist_wheel %1 %2 %3 %4
dir /s /b dist\*.whl
