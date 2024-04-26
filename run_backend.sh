#!/bin/bash

BACKEND_SCRIPT_PATH="reverie/backend_server"
BACKEND_SCRIPT_FILE="reverie.py"
CONDA_ENV="simulacra"
echo "Running backend server"
cd ${BACKEND_SCRIPT_PATH}
source /home/${USER}/anaconda3/bin/activate ${CONDA_ENV}
python3 ${BACKEND_SCRIPT_FILE}