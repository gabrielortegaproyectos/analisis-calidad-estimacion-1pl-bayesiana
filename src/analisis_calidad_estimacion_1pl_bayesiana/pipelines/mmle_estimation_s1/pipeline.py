from kedro.pipeline import Pipeline, node

from .nodes import mmle_estimate_for_mask, summarize_mmle_estimation


def create_pipeline(**kwargs) -> Pipeline:
    """Pipeline MMLE estimation sobre subsamples (S1).

    - Inputs: responses (completo) y 10 máscaras persistidas
    - Output: 10 CSVs de dificultades estimadas por máscara + 1 resumen global
    """
    percents = kwargs.get("percents", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

    nodes = []
    est_output_names = []

    for p in percents:
        key = str(p).replace('.', '_')
        mask_name = f"subsample_mask_p_{key}"
        out_name = f"mmle_estimation_difficulty_p_{key}"
        est_output_names.append((p, out_name))

        nodes.append(
            node(
                func=mmle_estimate_for_mask,
                inputs=dict(
                    responses="sample__s1.responses",
                    mask=f"subsample__s1.{mask_name}",
                ),
                outputs=out_name,
                name=f"s1_mmle_estimate_for_{mask_name}",
                tags={"sample_1", "mmle", "estimation"},
            )
        )

    # Summary node
    summary_inputs = {"difficulties": "sample__s1.difficulties"}
    for p, out_name in est_output_names:
        summary_inputs[f"est_p_{str(p).replace('.', '_')}"] = out_name

    nodes.append(
        node(
            func=summarize_mmle_estimation,
            inputs=summary_inputs,
            outputs="mmle_estimation_summary",
            name="s1_mmle_estimation_summary",
            tags={"sample_1", "mmle", "estimation"},
        )
    )

    return Pipeline(nodes)
