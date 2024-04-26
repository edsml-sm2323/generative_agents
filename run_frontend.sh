#!/bin/bash

FRONTEND_SCRIPT="environment/frontend_server/manage.py"
CONDA_ENV="simulacra"
echo "Running frontend server"
source /home/${USER}/anaconda3/bin/activate ${CONDA_ENV}
python ${FRONTEND_SCRIPT} runserver