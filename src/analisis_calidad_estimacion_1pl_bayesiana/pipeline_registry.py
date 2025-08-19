"""Project pipelines."""
from __future__ import annotations

from kedro.pipeline import Pipeline
from kedro.pipeline.modular_pipeline import pipeline as modular_pipeline

from analisis_calidad_estimacion_1pl_bayesiana.pipelines.sample_s1 import (
    create_pipeline as create_sample_s1,
)


def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    s1 = create_sample_s1()
    s1_ns = modular_pipeline(s1, namespace="sample__s1").tag({"sample", "sample_1"})

    return {
        "sample_s1": s1_ns,
        "__default__": s1_ns,
    }
