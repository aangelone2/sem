#!/bin/bash

if [[ $SEM_TEST == 1 ]]
then
  python -m modules.main &
  sleep 2
  python -m pytest -x -s -v .
else
  python -m modules.main
fi
