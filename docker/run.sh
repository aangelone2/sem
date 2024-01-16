#!/bin/bash

if [[ $SEM_LAUNCH == "docs" ]]
then
  mkdocs build
  mkdocs serve
else
  python -m modules.main
fi
