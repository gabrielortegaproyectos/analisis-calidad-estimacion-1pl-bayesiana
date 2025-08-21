from kedro.pipeline import Pipeline, node

from .nodes import bayes_estimate_for_mask_and_prior, summarize_bayes_estimation


def create_pipeline(**kwargs) -> Pipeline:
    """Pipeline Bayes estimation sobre grid (masks x predicciones) en S1.

    - Inputs: responses, difficultés, 10 máscaras y 10 predicciones
    - Output: 100 CSVs de dificultades estimadas + 1 resumen global
    """
    percents = kwargs.get("percents", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    r_levels = kwargs.get("r_levels", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

    nodes = []
    est_output_names: list[tuple[str, str]] = []

    for p in percents:
        p_key = str(p).replace('.', '_')
        mask_ds = f"subsample__s1.subsample_mask_p_{p_key}"
        for r in r_levels:
            r_key = str(r).replace('.', '_')
            pred_ds = f"auto_pred__s1.pred_difficulty_r_{r_key}"
            out_name = f"bayes_estimation_difficulty_p_{p_key}_r_{r_key}"
            est_output_names.append((f"est_p_{p_key}_r_{r_key}", out_name))

            nodes.append(
                node(
                    func=bayes_estimate_for_mask_and_prior,
                    inputs=dict(
                        responses="sample__s1.responses",
                        mask=mask_ds,
                        prior_pred=pred_ds,
                        sigma_prior_override="params:sigma_prior_override",
                        base_stat_variance="params:base_stat_variance",
                        draws="params:draws",
                        tune="params:tune",
                        chains="params:chains",
                        target_accept="params:target_accept",
                        seed="params:seed",
                    ),
                    outputs=out_name,
                    name=f"s1_bayes_estimate_p_{p_key}_r_{r_key}",
                    tags={"sample_1", "bayes", "estimation"},
                )
            )

    # Summary node
    summary_inputs = {"difficulties": "sample__s1.difficulties"}
    for key, out_name in est_output_names:
        summary_inputs[key] = out_name

    nodes.append(
        node(
            func=summarize_bayes_estimation,
            inputs=summary_inputs,
            outputs="bayes_estimation_summary",
            name="s1_bayes_estimation_summary",
            tags={"sample_1", "bayes", "estimation"},
        )
    )

    return Pipeline(nodes)
