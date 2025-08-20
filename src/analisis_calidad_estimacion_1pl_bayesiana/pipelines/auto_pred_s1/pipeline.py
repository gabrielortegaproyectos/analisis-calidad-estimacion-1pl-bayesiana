from functools import partial, update_wrapper
from kedro.pipeline import Pipeline, node

from .nodes import generate_predicted_difficulties_for_r, summarize_pred_discrimination


def create_pipeline(**kwargs) -> Pipeline:
    """Pipeline de generación automática de predicciones de dificultad (S1).

    - Input: difficulties (de sample 1)
    - Params: seed
    - Output: 10 datasets persistentes: pred_difficulty_r_0_1, ..., pred_difficulty_r_1_0
    """

    r_levels = [
        0.1, 0.2, 0.3, 0.4, 0.5,
        0.6, 0.7, 0.8, 0.9, 1.0,
    ]

    nodes = []
    for r in r_levels:
        out_name = f"pred_difficulty_r_{str(r).replace('.', '_')}"
        # Envolver el partial para mejorar el logging en Kedro
        func = partial(generate_predicted_difficulties_for_r, discrimination=r)
        update_wrapper(func, generate_predicted_difficulties_for_r)
        nodes.append(
            node(
                func=func,
                inputs=dict(
                    difficulties="difficulties",
                    seed="params:seed",
                ),
                outputs=out_name,
                name=f"s1_generate_pred_for_r_{str(r).replace('.', '_')}",
                tags={"sample_1", "auto_pred"},
            )
        )

    # Nodo de resumen de discriminación lograda (corr y corr^2) para todos los outputs
    summary_inputs = {
        "difficulties": "difficulties",
        "pred_r_0_1": "pred_difficulty_r_0_1",
        "pred_r_0_2": "pred_difficulty_r_0_2",
        "pred_r_0_3": "pred_difficulty_r_0_3",
        "pred_r_0_4": "pred_difficulty_r_0_4",
        "pred_r_0_5": "pred_difficulty_r_0_5",
        "pred_r_0_6": "pred_difficulty_r_0_6",
        "pred_r_0_7": "pred_difficulty_r_0_7",
        "pred_r_0_8": "pred_difficulty_r_0_8",
        "pred_r_0_9": "pred_difficulty_r_0_9",
        "pred_r_1_0": "pred_difficulty_r_1_0",
    }

    nodes.append(
        node(
            func=summarize_pred_discrimination,
            inputs=summary_inputs,
            outputs="pred_discrimination_summary",
            name="s1_summarize_pred_discrimination",
            tags={"sample_1", "auto_pred"},
        )
    )

    return Pipeline(nodes)
