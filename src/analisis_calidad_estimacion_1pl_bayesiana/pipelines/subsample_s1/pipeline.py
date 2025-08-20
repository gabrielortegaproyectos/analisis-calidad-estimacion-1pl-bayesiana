from kedro.pipeline import Pipeline, node
from functools import partial, update_wrapper

from .nodes import generate_random_subsample_mask


def create_pipeline(**kwargs) -> Pipeline:
    """Genera máscaras de subsample aleatorio para porcentajes de N total.

    - Lee n_total (número de estudiantes) y seed desde parámetros.
    - Lee percents (lista de fracciones 0..1) y genera tamaños = round(n_total * p).
    - Crea un nodo por tamaño, guarda CSV con la máscara (0/1).
    Tags: {"sample_1", "random_subsample"}
    """
    # Por comodidad también soportamos percents por defecto si se ejecuta sin registry
    percents = kwargs.get("percents", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

    # Los tamaños reales se calcularán en tiempo de ejecución según n_total
    # Aquí sólo definimos el esqueleto de nodos; los outputs usan el tamaño calculado

    nodes = []

    # Creamos nodos para cada percent, y el tamaño final se calcula dentro del partial
    for i, p in enumerate(percents):
        p = float(p)

        def make_node(percent: float):
            def bind_n_selected(n_total: int, seed):
                # Kedro pasará n_total y seed como inputs; calculamos n_selected aquí
                n_selected = int(round(n_total * percent))
                return generate_random_subsample_mask(n_total=n_total, n_selected=n_selected, seed=seed)

            return bind_n_selected

        func = make_node(p)
        update_wrapper(func, generate_random_subsample_mask)

        # El nombre del output incorpora el percent para estabilidad (independiente de n_total)
        out_name = f"subsample_mask_p_{str(p).replace('.', '_')}"

        nodes.append(
            node(
                func=func,
                inputs=dict(n_total="params:n_total", seed="params:seed"),
                outputs=out_name,
                name=f"s1_generate_subsample_mask_p_{str(p).replace('.', '_')}",
                tags={"sample_1", "random_subsample"},
            )
        )

    return Pipeline(nodes)
