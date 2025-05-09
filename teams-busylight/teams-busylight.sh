#!/bin/bash

VENV_DIR=[path to venv]
PY_SCRIPT=[path to python script]

if [ ! -f ${VENV_DIR}/bin/activate ]
then
  echo "Error: Setup python virtual env and set VENV_DIR"
  exit 1
fi

. ${VENV_DIR}/bin/activate
python ${PY_SCRIPT}
