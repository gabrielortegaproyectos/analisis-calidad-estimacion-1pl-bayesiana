"""
This is a boilerplate pipeline 'generate_responses'
generated using Kedro 0.19.14
"""

"""Nodes for the generate_responses pipeline."""
import numpy as np
import pandas as pd

def generate_parameters(n_items: int, n_persons: int, seed: int = 8927):
    """Generate item difficulties and person abilities."""
    rng = np.random.default_rng(seed)
    item_difficulties = rng.normal(0, 1, n_items)
    person_abilities = rng.normal(0, 1, n_persons)
    # Convert to DataFrame for compatibility with Kedro
    item_difficulties_df = pd.DataFrame(item_difficulties, columns=["difficulty"])
    person_abilities_df = pd.DataFrame(person_abilities, columns=["ability"])
    return item_difficulties_df, person_abilities_df

def simulate_responses(item_difficulties, person_abilities, seed: int = 8927):
    """Simulate responses based on item difficulties and person abilities."""
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    rng = np.random.default_rng(seed)
    # Ensure data is in float64 format
    item_difficulties = item_difficulties["difficulty"].astype(float).values
    person_abilities = person_abilities["ability"].astype(float).values

    n_persons = len(person_abilities)
    n_items = len(item_difficulties)
    responses = np.zeros((n_persons, n_items))
    for i, theta in enumerate(person_abilities):
        p = sigmoid(theta - item_difficulties)
        responses[i, :] = rng.binomial(1, p)
    responses_df = pd.DataFrame(responses, columns=[f"Item_{j+1}" for j in range(n_items)])
    return responses_df
