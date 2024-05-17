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


def get_new_checkpoint(step: int, tot_steps: int, checkpoint_freq: int) -> int:
    """Get the current checkpoint from the checkpoint file

    Args:
        step (int): The current step.
        tot_steps (int): The total steps to run.
        checkpoint_freq (int): The frequency of the checkpoints.

    Returns:
        int: The new checkpoint.
    """
    new_checkpoint = step + checkpoint_freq
    if new_checkpoint > tot_steps:
        new_checkpoint = tot_steps
    return new_checkpoint


def save_checkpoint(rs, idx: int) -> Tuple[str, int, int]:
    """Save the checkpoint and return the data to start the new one.

    Args:
        rs (ReverieServer): The reverie server object.
        idx (int): The index of the checkpoint.
    
    Returns:
        Tuple[str, int, int]: The name of the new experiment, the starting step and the index of the checkpoint.
    """
    target = rs.sim_code
    rs.open_server(input_command="fin")
    print(f"Checkpoint saved: {target}", flush=True)    
    return target, get_starting_step(target), idx+1
    

if __name__ == '__main__':
    checkpoint_freq = 200 # 1 step = 10 sec
    log_path = "cost-logs"
    idx = 0
    origin, target, tot_steps = parse_args()
    current_step = get_starting_step(origin)
    exp_name = target
    start_time = datetime.now()
    tot_steps = int(tot_steps)
    curr_checkpoint = get_new_checkpoint(current_step, tot_steps, checkpoint_freq)
    
    print(f"Origin: {origin}")
    print(f"Target: {target}")
    print(f"Total steps: {tot_steps}")
    
    while current_step < tot_steps:
        try:
            steps_to_run = curr_checkpoint - current_step
            target = f"{exp_name}-s-{idx}-{current_step}-{curr_checkpoint}"
            print(f"Running experiment '{exp_name}' from step '{current_step}' to '{curr_checkpoint}'", flush=True)
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
                origin, current_step, idx = save_checkpoint(rs, idx)
            else:
                # delete the experiment
                shutil.rmtree(f"../../environment/frontend_server/storage/{target}")
            print(f"Error at step {current_step}", flush=True)
        else:
            origin, current_step, idx = save_checkpoint(rs, idx)
            curr_checkpoint = get_new_checkpoint(current_step, tot_steps, checkpoint_freq)

    print(f"Experiment finished: {exp_name}")
    print(f"Execution time: {datetime.now() - start_time}")
    OpenAICostLoggerViz.print_experiment_cost(experiment=exp_name, path=log_path)
    OpenAICostLoggerViz.print_total_cost(path=log_path)