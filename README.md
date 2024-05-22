

# Generative Agents: Interactive Simulacra of Human Behavior 

<p align="center" width="100%">
<img src="cover.png" alt="Smallville" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p>

This repository contains fixes and improvements for the repository "[generative_agents](https://github.com/joonspk-research/generative_agents)" that accompanies the paper "[Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442)."

Since the project is no longer officially supported, I decided to develop some new features:
- [x] Easy configuration + **Azure support**
- [x] **Cost tracking** using [openai-cost-logger](https://github.com/drudilorenzo/openai-cost-logger)
- [x] Set **cost upperbound** and stop the experiment when it is reached
- [x] New models and OpenAI API support
- [x] Added [skip-morning-s-14](https://github.com/drudilorenzo/generative_agents/tree/fix-and-improve/environment/frontend_server/storage/skip-morning-s-14): a simulation based on `base_the_ville_n25` that starts after 3000 steps (~8:00am). That permits us to save time and see interactions and actions earlier.

## Setting Up The Environment

### Step 1. Conda Env

Do not change the env name to be able to use the bash scripts later.
```bash
    conda create -n simulacra python=3.9.12 pip
    conda activate simulacra
    pip install -r requirements.txt
```

### Step 2. OpenAI Config

Create a file called `openai_config.json` in the root directory.\
Azure example:
```json
{
    "client": "azure", 
    "model": "gpt-35-turbo-0125",
    "model-key": "<MODEL-KEY>",
    "model-endpoint": "<MODEL-ENDPOINT>",
    "model-api-version": "<API-VERSION>",
    "model-costs": {
        "input":  0.5,
        "output": 1.5
    },
    "embeddings-client": "azure",
    "embeddings": "text-embedding-3-small",
    "embeddings-key": "<EMBEDDING-KEY>",
    "embeddings-endpoint": "<EMBEDDING-MODEL-ENDPOINT>",
    "embeddings-api-version": "<API-VERSION>",
    "embeddings-costs": {
        "input": 0.02,
        "output": 0.0
    },
    "experiment-name": "simulacra-test",
    "cost-upperbound": 10
}
```
OpenAI example:
```json
{
    "client": "openai", 
    "model": "gpt-3.5-turbo-0125",
    "model-key": "<MODEL-KEY>",
    "model-costs": {
        "input":  0.5,
        "output": 1.5
    },
    "embeddings-client": "openai",
    "embeddings": "text-embedding-3-small",
    "embeddings-key": "<EMBEDDING-KEY>",
    "embeddings-costs": {
        "input": 0.02,
        "output": 0.0
    },
    "experiment-name": "simulacra-test",
    "cost-upperbound": 10
}
```

Feel free to change and test also other models (and change accordingly the input and output costs).\
Be aware that the only supported clients are **azure** and **openai**.\
The generation and the embedding models are configured separately to be able to use different clients.\
Change also the `cost-upperbound` according to your needs (the cost computation is done using "[openai-cost-logger](https://github.com/drudilorenzo/openai-cost-logger)" and the costs are specified per million tokens).

## Running a simulation

### Step 1. Starting the Environment Server
```bash
    ./run_frontend.sh
```

### Step 2. Starting the Simulation Server
```bash
    ./run_backend.sh <ORIGIN> <TARGET>
```
Example:
```bash
    ./run_backend.sh base_the_ville_isabella_maria_klaus simulation-test
```

### Endpoint list
- [http://localhost:8000/](http://localhost:8000/) - check if the server is running
- [http://localhost:8000/simulator_home](http://localhost:8000/simulator_home) - watch the live simulation
- `http://localhost:8000/replay/<simulation-name>/<starting-time-step>` - replay a simulation

For a more detailed explanation see the [original readme](README_origin.md).


## Cost Tracking

For the cost tracking is used the package "[openai-cost-logger](https://github.com/drudilorenzo/openai-cost-logger)". Given the possible high cost of a simulation,  you can set a cost upperbound in the config file to be able to raise an exception and stop the execution when it is reached.

See all the details of your expenses using the notebook "[cost_viz.ipynb](https://github.com/drudilorenzo/generative_agents/blob/main/cost_viz.ipynb)."

## Cost Assessment

### 1. base_the_ville_isabella_maria_klaus

- **Model**: "gpt-3.5-turbo-0125"
- **Embeddings**: "text-embedding-3-small"
- **N. Agents**: 3
- **Steps**: ~5000
- **Final Cost**: ~0.31 USD

### 2. base_the_ville_n25

- See the simulation saved: [skip-morning-s-14](https://github.com/drudilorenzo/generative_agents/tree/fix-and-improve/environment/frontend_server/storage/skip-morning-s-14)
- **Model**: "gpt-3.5-turbo-0125"
- **Embeddings**: "text-embedding-3-small"
- **N. Agents**: 25
- **Steps**: ~3000 (until ~8 a.m.)
- **Final Cost**: ~1.3 USD

### 3. base_the_ville_n25

- **Model**: "gpt-3.5-turbo-0125"
- **Embeddings**: "text-embedding-3-small"
- **N. Agents**: 25
- **Steps**: ~8650 (full day)
- **Final Cost**: ~18.5 USD

## TO-FIX/TO-BE-DONE
Although this repo contains numerous fixes, here are some problems that have not yet been resolved or new features I would like to add:
- [ ] joonspk-research/generative_agents#111: Still have to understand when it happens (in my case it happens after lots of steps like 4/5000) - [screen](https://github.com/drudilorenzo/generative_agents/blob/main/current-bugs/1.png)
- [ ] joonspk-research/generative_agents#27: Add zoom in/out
