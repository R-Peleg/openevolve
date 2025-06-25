"""
A small evaluation script to put in the wordpl repository and execute in subprocess.
"""
import numpy as np
import json
from evaluate import evaluate_once

class MyStrategy:
    ...

# Will be replaced by the strategy definition from the initial program.
#STRATEGY_DEF#

if __name__ == "__main__":
    results = []
    for _ in range(10):
        # Run the evaluation with the strategy defined above.
        total_budget = evaluate_once(MyStrategy(), False)
        results.append(total_budget)
    result_dict = {
        "total_budget_score": 1000 - np.median(total_budget),
    }
    print(json.dumps(result_dict, indent=4))
