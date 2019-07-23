#!/bin/bash
rm -rf build
rm -rf dist
rm -rf namedstruct.egg-info

python3 setup.py sdist bdist_wheel "$@"
ls -l dist/*.whl
