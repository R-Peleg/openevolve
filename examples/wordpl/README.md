# Word PL
This example show how OpenEvolve can be used to solve privacy challenge in Wordle game.

## Setup
First, close the Wordpl repository:
```bash
cd examples/wordpl
git clone https://github.com/TedTed/wordpl.git
```

Then, initialize venv and install requirements:
```bash
cd wordpl
python3 -m virtualenv venv
source venv/bin/activate
pip install numpy pandas tqdm numba
```

## Run
Run OpenEvolve with the following command:
```bash
python openevolve-run.py --config examples/wordpl/config.yaml examples/wordpl/initial_program.py examples/wordpl/evaluate.py --iterations 10
```