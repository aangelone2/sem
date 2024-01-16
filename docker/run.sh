#!/bin/bash

if [[ $SEM_LAUNCH == "test" ]]
then
  python -m pytest -x -s -v .
elif [[ $SEM_LAUNCH == "docs" ]]
then
  mkdocs build
  mkdocs serve
else
  python -m modules.main
fi
