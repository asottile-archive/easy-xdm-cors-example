#/usr/bin/env bash

export PYTHONPATH='.'

coverage erase
coverage run fix_coverage.py
coverage run `which testify` tests $@
coverage combine
coverage report -m --omit=/usr/*,*/__init__.py,tests/*,pre-commit.py,*_mako
exit $?
