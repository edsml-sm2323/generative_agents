#!/usr/bin/env python3

import os
import sys
import json
import time
import shutil
import reverie
import argparse
import threading
import webbrowser
from typing import Tuple
from pathlib import Path
from datetime import datetime
from openai_cost_logger import OpenAICostLoggerViz


def parse_args() -> Tuple[str, str]:
    """Parse bash arguments

    Returns:
        Tuple[str, str, int]:
            - name of the forked simulation
            - the name of the new simulation
            - total steps to run (step = 10sec in the simulation)
    """
    parser = argparse.ArgumentParser(description='Reverie Server')
    parser.add_argument(
    '--origin',
    type=str,
    default="base_the_ville_isabella_maria_klaus",
    help='The name of the forked simulation'
    )
    parser.add_argument(
    '--target',
    type=str,
    default="test-simulation",
    help='The name of the new simulation'
    )
    parser.add_argument(
        '--steps',
        type=str,
        default="8640", # 24 hours
        help='Total steps to run'
    )
    origin = parser.parse_args().origin
    target = parser.parse_args().target
    steps = parser.parse_args().steps
    return origin, target, steps


def get_starting_step(exp_name: str) -> int:
    """Get the starting step of the experiment. 

    Returns:
        exp_name (str): The name of the experiment
    """
    current_step = 0
    experiments_directory = "../../environment/frontend_server/storage"
    full_path = Path(experiments_directory, exp_name, "movement")  
    if full_path.exists():
        files = os.listdir(full_path)
        steps = [int(os.path.splitext(filename)[0]) for filename in files]
        print(f"Steps: {steps}", flush=True)
        current_step = max(steps)
    return current_step


def start_web_tab() -> None:
    """Open a new tab in the browser with the simulator home page"""
    url = "http://localhost:8000/simulator_home"
    chrome_path = '/usr/bin/google-chrome %s'
    print("Opening the simulator home page", flush=True)
    time.sleep(15)
    webbrowser.get(chrome_path).open(url, new=2)

def get_exp_name () -> None:
    """Set the experiment name in the openai_config.json file

    Returns:
        exp_name (str): The name of the experiment
    """
    config_path = Path("../../openai_config.json")
    with open(config_path, "r") as f:
        openai_config = json.load(f) 
    return openai_config["experiment-name"]

if __name__ == '__main__':
    log_path = "cost-logs"
    origin, target, tot_steps = parse_args()
    current_step = get_starting_step(origin)
    exp_name = get_exp_name()
    start_time = datetime.now()
    tot_steps = int(tot_steps)
    idx = 0
    
    print(f"Origin: {origin}")
    print(f"Target: {target}")
    
    while current_step < tot_steps:
        try:
            steps_to_run = tot_steps - current_step
            target = f"{exp_name}-s-{idx}"
            print(f"Running experiment '{target}' from step '{current_step}' to '{tot_steps}'", flush=True)
            rs = reverie.ReverieServer(origin, target)
            th = threading.Thread(target=start_web_tab)
            th.start()
            rs.open_server(input_command=f"run {steps_to_run}")
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the experiment.")
            sys.exit(0)
        except Exception as e:
            print(e.args[0], flush=True)
            step = e.args[1]
            if step != 0:
                rs.open_server(input_command="fin")
                origin = target
                current_step = get_starting_step(origin)
                idx += 1
            else:
                # delete the experiment
                shutil.rmtree(f"../../environment/frontend_server/storage/{target}")
            print(f"Error at step {current_step}", flush=True)
        else:
            rs.open_server(input_command="fin")
            break

    print(f"Experiment finished: {exp_name}")
    print(f"Execution time: {datetime.now() - start_time}")
    OpenAICostLoggerViz.print_experiment_cost(experiment=exp_name, path=log_path)
    OpenAICostLoggerViz.print_total_cost(path=log_path)