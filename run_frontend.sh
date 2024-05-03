#!/bin/bash

FRONTEND_SCRIPT_PATH="environment/frontend_server"
FRONTEND_SCRIPT_FILE="manage.py"
CONDA_ENV="simulacra"

echo "Running frontend server"
cd ${FRONTEND_SCRIPT_PATH}
source /home/${USER}/anaconda3/bin/activate ${CONDA_ENV}

python ${FRONTEND_SCRIPT_FILE} runserver