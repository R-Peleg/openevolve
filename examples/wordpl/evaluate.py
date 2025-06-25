
import subprocess
import json
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORDPL_DIR = os.path.join(CURRENT_DIR, 'wordpl')

def evaluate(code_path):
    with open(code_path, 'r') as file:
        startegy_code = file.read()
    with open(os.path.join(CURRENT_DIR, 'evaluation_script.py'), 'r') as file:
        evaluation_script = file.read()
    evaluation_script = evaluation_script.replace('#STRATEGY_DEF#', startegy_code)
    evolve_eval_path = os.path.join(WORDPL_DIR, 'evolve_eval.py')
    with open(evolve_eval_path, 'w') as file:
        file.write(evaluation_script)
    
    venv_bin_dir_name = 'bin' if os.name == 'posix' else 'Scripts'
    wordpl_venv_interpreter = os.path.join(
        WORDPL_DIR, 'venv', venv_bin_dir_name, 'python')
    result = subprocess.run(
        [wordpl_venv_interpreter, evolve_eval_path],
        capture_output=True,
        text=True,
        cwd=WORDPL_DIR,
    )
    if result.returncode != 0:
        print(f"Error running the evaluation script: {result.stderr}")
        return {
            "total_budget_score": -1000,
            'validity': 0,
        }
    output = result.stdout.strip()
    try:
        result_dict = json.loads(output)
    except json.JSONDecodeError as e:
        return {
            "total_budget_score": -1000,
            'validity': 0,
        }
    return {
        'validity': 1000,
        **result_dict
    }


if __name__ == "__main__":
    # Run the evaluation on the cli arg
    import sys
    if len(sys.argv) != 2:
        print("Usage: python evaluate.py <path_to_strategy_code>")
        sys.exit(1)
    strategy_code_path = sys.argv[1]
    result = evaluate(strategy_code_path)
    print(json.dumps(result, indent=4))
