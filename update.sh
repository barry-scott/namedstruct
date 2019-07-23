#!/bin/bash
set -e
python3 -m twine check dist/*
python3 -m twine upload dist/*
