import numpy as np
import pandas as pd
from typing import Iterable


def generate_random_subsample_mask(n_total: int, n_selected: int, seed: int | None = None) -> pd.DataFrame:
    """Genera una máscara aleatoria de 0/1 de largo ``n_total`` con ``n_selected`` unos.

    Devuelve un DataFrame con una única columna ``mask`` y un índice de 0..n_total-1.
    """
    if n_selected > n_total:
        raise ValueError(f"n_selected={n_selected} no puede ser mayor que n_total={n_total}")

    rng = np.random.default_rng(seed)
    mask = np.zeros(int(n_total), dtype=int)
    idx = rng.choice(int(n_total), size=int(n_selected), replace=False)
    mask[idx] = 1
    return pd.DataFrame({"mask": mask})


def generate_multiple_subsamples(n_total: int, sizes: Iterable[int], seed: int | None = None) -> dict[str, pd.DataFrame]:
    """Genera múltiples máscaras para diferentes tamaños de subsample.

    Retorna un dict donde cada clave es ``size_<N>.csv`` y el valor el DataFrame de máscara.
    Útil si decidimos usar PartitionedDataset en el futuro.
    """
    out: dict[str, pd.DataFrame] = {}
    for i, n_selected in enumerate(sizes):
        s = None if seed is None else int(seed + i)
        out[f"size_{int(n_selected)}.csv"] = generate_random_subsample_mask(n_total, int(n_selected), seed=s)
    return out
