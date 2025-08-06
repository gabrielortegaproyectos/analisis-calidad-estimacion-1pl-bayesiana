"""
This is a boilerplate pipeline 'generate_responses'
generated using Kedro 0.19.14
"""

from kedro.pipeline import Pipeline, node

from .nodes import generate_parameters, simulate_responses


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=generate_parameters,
                inputs={
                    "n_items": "params:number_of_questions",
                    "n_persons": "params:number_of_students",
                },
                outputs=["difficulties_cience_1", "abilities_cience_1"],
                name="generate_parameters_node",
            ),
            node(
                func=simulate_responses,
                inputs={
                    "item_difficulties": "difficulties_cience_1",
                    "person_abilities": "abilities_cience_1",
                },
                outputs="responses_cience_1",
                name="simulate_responses_node",
            ),
        ]
    )
