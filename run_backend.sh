#!/bin/bash

BACKEND_SCRIPT_PATH="reverie/backend_server"
BACKEND_SCRIPT_FILE="reverie.py"
CONDA_ENV="simulacra"

# Delete the test dirs
WORKING_DIR="environment/frontend_server/storage/${2}/"
if [ -d "$WORKING_DIR" ]; then rm -rf ${WORKING_DIR} ; fi

echo "Running backend server at: http://127.0.0.1:8000/simulator_home"
cd ${BACKEND_SCRIPT_PATH}
source /home/${USER}/anaconda3/bin/activate ${CONDA_ENV}

python3 ${BACKEND_SCRIPT_FILE} --origin ${1} --target ${2}