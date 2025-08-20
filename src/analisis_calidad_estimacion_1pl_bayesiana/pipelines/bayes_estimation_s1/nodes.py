import logging
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    import pymc as pm
    import pytensor.tensor as pt
except Exception as e:  # pragma: no cover
    pm = None  # type: ignore
    pt = None  # type: ignore
    logger.warning("PyMC no disponible: %s", e)


def _filter_responses_with_mask(responses: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    if "mask" not in mask.columns:
        raise ValueError("La máscara debe tener una columna 'mask'.")
    resp = responses.sort_values("person_id").reset_index(drop=True)
    m = mask["mask"].to_numpy().astype(int)
    if m.size != resp.shape[0]:
        raise ValueError(f"Tamaño de máscara {m.size} no coincide con n_responses={resp.shape[0]}")
    selected = resp[m == 1].reset_index(drop=True)
    return selected


def _responses_matrix(filtered_responses: pd.DataFrame) -> np.ndarray:
    if "person_id" not in filtered_responses.columns:
        raise ValueError("Se espera columna 'person_id' en responses.")
    X = filtered_responses.drop(columns=["person_id"]).to_numpy(dtype=int)
    return X  # [persons x items]


def bayes_estimate_for_mask_and_prior(
    responses: pd.DataFrame,
    mask: pd.DataFrame,
    prior_pred: pd.DataFrame,
    sigma_prior_override: float | None,
    base_stat_variance: float,
    draws: int,
    tune: int,
    chains: int,
    target_accept: float,
    seed: int | None = None,
) -> pd.DataFrame:
    """Estima b por MCMC con prior N(mu=prior_pred, sigma).

    sigma = sigma_prior_override si no es None; si no, sqrt(base_stat_variance).
    prior_pred: DF [item_id, predicted_difficulty]
    Devuelve DF [item_id, est_bayes_difficulty]
    """
    if pm is None:
        raise RuntimeError("PyMC no está instalado en el entorno.")

    filt = _filter_responses_with_mask(responses, mask)
    Y = _responses_matrix(filt)  # persons x items
    n_persons, n_items = int(Y.shape[0]), int(Y.shape[1])

    pred = prior_pred.sort_values("item_id").reset_index(drop=True)
    mu_b = pred["predicted_difficulty"].to_numpy(dtype=float)
    if mu_b.shape[0] != n_items:
        # alinear si hay discrepancia
        item_cols = [c for c in filt.columns if c != "person_id"]
        item_ids = np.arange(1, len(item_cols) + 1, dtype=int)
        pred2 = pd.DataFrame({"item_id": item_ids}).merge(pred, on="item_id", how="left")
        mu_b = pred2["predicted_difficulty"].to_numpy(dtype=float)

    sigma_prior_b = float(sigma_prior_override) if sigma_prior_override is not None else float(np.sqrt(max(base_stat_variance, 0.0)))

    coords = {"person": np.arange(n_persons), "item": np.arange(n_items)}

    with pm.Model(coords=coords) as model:
        theta = pm.Normal("theta", mu=0.0, sigma=1.0, dims="person")
        b = pm.Normal("b", mu=mu_b, sigma=sigma_prior_b, dims="item")
        lin = theta[:, None] - b[None, :]
        p = pm.Deterministic("p", pm.math.sigmoid(lin))
        pm.Bernoulli("responses", p=p, observed=Y)

        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=float(target_accept),
            random_seed=seed,
            progressbar=False,
            cores=min(chains, 2),
        )

    b_hat = idata.posterior["b"].mean(dim=("chain", "draw")).values
    out = pd.DataFrame({"item_id": np.arange(1, n_items + 1, dtype=int), "est_bayes_difficulty": b_hat})
    return out


def summarize_bayes_estimation(
    difficulties: pd.DataFrame,
    **estimates: pd.DataFrame,
) -> pd.DataFrame:
    true_df = difficulties.sort_values("item_id").reset_index(drop=True)

    rows: list[dict] = []
    for key, est_df in sorted(estimates.items()):
        # key formato: est_p_0_3_r_0_7
        try:
            tmp = key.split("est_p_")[-1]
            p_str, r_str = tmp.split("_r_")
            percent = float(p_str.replace("_", "."))
            r_level = float(r_str.replace("_", "."))
        except Exception:
            percent = float("nan")
            r_level = float("nan")

        est_df = est_df.sort_values("item_id").reset_index(drop=True)
        merged = pd.merge(true_df, est_df, on="item_id", how="inner")
        y_true = merged["difficulty"].to_numpy(dtype=float)
        y_hat = merged["est_bayes_difficulty"].to_numpy(dtype=float)

        if y_true.size < 2 or np.all(~np.isfinite(y_hat)):
            r = np.nan
            r2 = np.nan
            mse = np.nan
            mae = np.nan
            bias = np.nan
        else:
            r = float(np.corrcoef(y_true, y_hat)[0, 1])
            r2 = r * r
            err = y_hat - y_true
            mse = float(np.mean(err ** 2))
            mae = float(np.mean(np.abs(err)))
            bias = float(np.mean(err))

        rows.append({
            "dataset_key": key,
            "percent": percent,
            "r_level": r_level,
            "r": r,
            "r2": r2,
            "mse": mse,
            "mae": mae,
            "bias": bias,
            "n_items": int(y_true.size),
        })

    return pd.DataFrame(rows).sort_values(["percent", "r_level"]).reset_index(drop=True)
