#!/bin/bash

BACKEND_SCRIPT_PATH="reverie/backend_server"
BACKEND_SCRIPT_FILE="automatic_execution.py"
CONDA_ENV="simulacra"
LOGS_PATH="../../logs"

FILE_NAME="Bash-Script"
echo "(${FILE_NAME}): Running backend server at: http://127.0.0.1:8000/simulator_home"
cd ${BACKEND_SCRIPT_PATH}
source /home/${USER}/anaconda3/bin/activate ${CONDA_ENV}

ARGS=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --origin|-o)
            ARGS="${ARGS} --origin ${2}"
            shift
            shift
            ;;
        --target|-t)
            ARGS="${ARGS} --target ${2}"
            shift
            shift
            ;;
        --steps|-s)
            ARGS="${ARGS} --steps ${2}"
            shift
            shift
            ;;
        --ui)
            ARGS="${ARGS} --ui ${2}"
            shift
            shift
            ;;
        --browser_path|-bp)
            ARGS="${ARGS} --browser_path ${2}"
            shift
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters
echo "(${FILE_NAME}): Arguments: ${ARGS}"

timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
echo "(${FILE_NAME}): Timestamp: ${timestamp}"
mkdir -p ${LOGS_PATH}
python3 ${BACKEND_SCRIPT_FILE} ${ARGS} | tee  ${LOGS_PATH}/${2}_${timestamp}.txt