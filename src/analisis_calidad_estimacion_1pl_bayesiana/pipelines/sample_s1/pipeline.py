"""Pipeline de sample 1 (S1).

Este pipeline genera:
- difficulties: dificultades de ítems (persistido como CSV en data/02_intermediate/sample__s1/)
- abilities: habilidades de personas (persistido como CSV en data/02_intermediate/sample__s1/)
- responses: respuestas simuladas 1PL (persistido como CSV en data/02_intermediate/sample__s1/)

Notas sobre tags:
Se usan dos tags en cada nodo, {"sample", "sample_1"}, para poder:
- Ejecutar/filtrar todos los pipelines de muestra con la tag general "sample".
- Ejecutar/filtrar específicamente el sample 1 con la tag "sample_1".
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    generate_difficulties_s1,
    generate_abilities_s1,
    simulate_responses_s1,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Crea el pipeline S1 con tres nodos: dificultades, habilidades y respuestas.

    Los datasets de salida (difficulties, abilities, responses) se configuran en el
    catálogo para persistirse bajo data/02_intermediate/sample__s1/.
    """
    nodes = []

    # Generar dificultades de ítems (sample 1)
    nodes.append(
        node(
            func=generate_difficulties_s1,
            inputs=dict(
                n_items="params:test_parameters.number_of_questions",
                stat_difficulty="params:test_parameters.stat_difficulty",
                seed="params:seed",
            ),
            outputs="difficulties",
            name="s1_generate_difficulties",
            tags={"sample", "sample_1"},  # ver nota en el docstring superior
        )
    )

    # Generar habilidades de personas (sample 1)
    nodes.append(
        node(
            func=generate_abilities_s1,
            inputs=dict(
                n_persons="params:student_parameters.number_of_students",
                theta_distribution="params:student_parameters.theta_distribution",
                seed="params:seed",
            ),
            outputs="abilities",
            name="s1_generate_abilities",
            tags={"sample", "sample_1"},  # ver nota en el docstring superior
        )
    )

    # Simular respuestas (sample 1)
    nodes.append(
        node(
            func=simulate_responses_s1,
            inputs=dict(
                item_difficulties="difficulties",
                person_abilities="abilities",
                seed="params:seed",
            ),
            outputs="responses",  # antes: "responses_full"
            name="s1_simulate_responses",
            tags={"sample", "sample_1"},  # ver nota en el docstring superior
        )
    )

    return Pipeline(nodes)
