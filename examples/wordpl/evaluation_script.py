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
    # Use the the robbins monro algorithm to estimate the budget leading to 50% successs rate.
    guess = 36.9
    C = 1
    epsilon = 1e-4
    for n in range(100):
        # Run the evaluation with the strategy defined above.
        used_budget = evaluate_once(MyStrategy(budget=guess), debug=False)
        score = int(used_budget <= guess + epsilon)
        guess = guess - (C / (n + 2)) * (score - 0.5)
    result_dict = {
        "minus_estimated_median_budget": -round(guess, 3),
    }
    print(json.dumps(result_dict, indent=4))
