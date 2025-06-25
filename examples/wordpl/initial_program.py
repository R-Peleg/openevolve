# Taken from https://github.com/TedTed/wordpl/blob/main/strategies/bayesian_greedy.py
# Inlined imports and changed class name to MyStrategy.

# A strategy identical to BayesianRandom (see bayesian_random.py), but instead
# of choosing each guess randomly, it samples from the prior distribution.

from dataclasses import dataclass
from math import exp
from random import uniform
import pandas as pd

with open("valid.txt", "r") as f:
    valid = f.read().splitlines()

with open("answers.txt", "r") as f:
    answers = f.read().splitlines()


# Check whether a given clue is consistent with a word.
def is_consistent(word, index, letter, clue):
    if clue == '.':
        return letter not in word
    if clue == 'i':
        return letter in word and word[index] != letter
    if clue == 'c':
        return word[index] == letter
    else:
        raise ValueError(f"Invalid clue '{clue}' for letter '{letter}' at index {index} in word '{word}'")


# Updates the weight associated with a word based on a clue
def update_weight(row, index, letter, clue, epsilon):
    if is_consistent(row["word"], index, letter, clue):
        return row["weight"]*exp(epsilon/5)
    return row["weight"]

def uniform_prior():
    prior = pd.DataFrame({"word": answers})
    prior["weight"] = 1
    return prior

def update_prior(prior, guess, epsilon, clues):
    for index, clue in enumerate(clues):
        prior["weight"] = prior.apply(
            lambda row: update_weight(row, index, guess[index], clue, epsilon),
            axis=1)
    # normalizing the distribution is not
    prior["weight"] = prior["weight"] / sum(prior["weight"])
    return prior


# Returns the input randomized up to ±10%
def jitter(x):
    return uniform(x*0.9, x*1.1)


@dataclass
class MyStrategy:
    epsilon: float = 25
    certainty: float = 0.9

    def first_move(self):
        self.prior = uniform_prior()
        first_guess = self.prior["word"].sample().item()
        self.past_guesses = [first_guess]
        return first_guess, jitter(self.epsilon)

    def next_move(self, guess, epsilon, clues):
        update_prior(self.prior, guess, epsilon, clues)
        # If we have a winner, return it as a final answer
        best_candidate = self.prior.loc[self.prior["weight"].idxmax()]
        if best_candidate["weight"] > self.certainty:
            return best_candidate["word"], 0
        # If not, sample from the prior distribution, minus words that were
        # already picked as prior guesses.
        possible_guesses = self.prior[~self.prior["word"].isin(self.past_guesses)]
        next_guess = possible_guesses["word"].sample(weights=possible_guesses["weight"])
        self.past_guesses.append(next_guess)
        return next_guess.item(), jitter(self.epsilon)
