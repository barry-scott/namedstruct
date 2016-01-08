rmdir /s /q build
rmdir /s /q dist
rmdir /s /q namedstruct.egg-info

py -3.5 setup.py sdist bdist_wheel
py -3.5 -m twine upload dist\*
