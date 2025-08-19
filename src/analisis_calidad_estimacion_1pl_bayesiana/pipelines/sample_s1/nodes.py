import logging
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_difficulties_s1(
    n_items: int,
    stat_difficulty: Dict[str, float],
    seed: int | None = None,
) -> pd.DataFrame:
    """Genera dificultades de ítems para el sample 1."""
    if seed is not None:
        np.random.seed(seed)
    mu = float(stat_difficulty.get("mean", 0.0))
    var = float(stat_difficulty.get("variance", 1.0))
    sd = float(np.sqrt(max(var, 0.0)))
    d = np.random.normal(mu, sd, int(n_items))
    df = pd.DataFrame({"item_id": np.arange(1, int(n_items) + 1), "difficulty": d})
    logger.info("[s1] Generated difficulties: n_items=%d, mu=%.3f, var=%.3f", int(n_items), mu, var)
    return df


def generate_abilities_s1(
    n_persons: int,
    theta_distribution: Dict[str, float],
    seed: int | None = None,
) -> pd.DataFrame:
    """Genera habilidades de personas para el sample 1."""
    if seed is not None:
        np.random.seed(seed + 1 if seed is not None else None)
    mu = float(theta_distribution.get("mean", 0.0))
    var = float(theta_distribution.get("variance", 1.0))
    sd = float(np.sqrt(max(var, 0.0)))
    t = np.random.normal(mu, sd, int(n_persons))
    df = pd.DataFrame({"person_id": np.arange(1, int(n_persons) + 1), "ability": t})
    logger.info("[s1] Generated abilities: n_persons=%d, mu=%.3f, var=%.3f", int(n_persons), mu, var)
    return df


def simulate_responses_s1(
    item_difficulties: pd.DataFrame,
    person_abilities: pd.DataFrame,
    seed: int | None = None,
) -> pd.DataFrame:
    """Simula respuestas binarias con modelo 1PL (discriminación=1)."""
    if seed is not None:
        np.random.seed(seed + 2 if seed is not None else None)

    item_difficulties = item_difficulties.sort_values("item_id")
    person_abilities = person_abilities.sort_values("person_id")

    n_items = int(item_difficulties.shape[0])
    diffs = item_difficulties["difficulty"].to_numpy()

    rows = []
    for pid, ability in zip(person_abilities["person_id"], person_abilities["ability" ]):
        logits = ability - diffs
        probs = 1.0 / (1.0 + np.exp(-logits))
        responses = (np.random.rand(n_items) < probs).astype(int)
        rows.append(np.concatenate([[pid], responses]))

    cols = ["person_id"] + [f"item_{i}" for i in range(1, n_items + 1)]
    responses_df = pd.DataFrame(rows, columns=cols)
    logger.info("[s1] Simulated responses: persons=%d, items=%d", len(person_abilities), n_items)
    return responses_df
