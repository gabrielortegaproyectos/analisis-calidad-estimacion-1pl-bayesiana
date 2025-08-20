"""Project pipelines."""
from __future__ import annotations

from kedro.pipeline import Pipeline, pipeline

from analisis_calidad_estimacion_1pl_bayesiana.pipelines.sample_s1 import (
    create_pipeline as create_sample_s1,
)
from analisis_calidad_estimacion_1pl_bayesiana.pipelines.auto_pred_s1 import (
    create_pipeline as create_auto_pred_s1,
)
from analisis_calidad_estimacion_1pl_bayesiana.pipelines.subsample_s1 import (
    create_pipeline as create_subsample_s1,
)
from analisis_calidad_estimacion_1pl_bayesiana.pipelines.mmle_estimation_s1 import (
    create_pipeline as create_mmle_estimation_s1,
)


def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    s1 = create_sample_s1()
    s1_ns = pipeline(s1, namespace="sample__s1").tag({"sample", "sample_1"})

    auto_pred = create_auto_pred_s1()
    auto_pred_ns = pipeline(
        auto_pred,
        namespace="auto_pred__s1",
        inputs={
            "difficulties": "sample__s1.difficulties",
        },
        parameters={
            "seed": "params:sample__s1.seed",
            # espacios reservados si en el futuro auto_pred usa otros params
        },
    ).tag({"sample", "sample_1", "auto_pred"})

    subsample = create_subsample_s1()
    subsample_ns = pipeline(
        subsample,
        namespace="subsample__s1",
        parameters={
            "seed": "params:sample__s1.seed",
            # n_total = number_of_students
            "n_total": "params:sample__s1.student_parameters.number_of_students",
        },
    ).tag({"sample", "sample_1", "random_subsample"})

    mmle = create_mmle_estimation_s1()
    mmle_ns = pipeline(
        mmle,
        namespace="mmle_estimation__s1",
        inputs={
            # datos originales
            "sample__s1.responses": "sample__s1.responses",
            "sample__s1.difficulties": "sample__s1.difficulties",
            # máscaras de subsample
            "subsample__s1.subsample_mask_p_0_1": "subsample__s1.subsample_mask_p_0_1",
            "subsample__s1.subsample_mask_p_0_2": "subsample__s1.subsample_mask_p_0_2",
            "subsample__s1.subsample_mask_p_0_3": "subsample__s1.subsample_mask_p_0_3",
            "subsample__s1.subsample_mask_p_0_4": "subsample__s1.subsample_mask_p_0_4",
            "subsample__s1.subsample_mask_p_0_5": "subsample__s1.subsample_mask_p_0_5",
            "subsample__s1.subsample_mask_p_0_6": "subsample__s1.subsample_mask_p_0_6",
            "subsample__s1.subsample_mask_p_0_7": "subsample__s1.subsample_mask_p_0_7",
            "subsample__s1.subsample_mask_p_0_8": "subsample__s1.subsample_mask_p_0_8",
            "subsample__s1.subsample_mask_p_0_9": "subsample__s1.subsample_mask_p_0_9",
            "subsample__s1.subsample_mask_p_1_0": "subsample__s1.subsample_mask_p_1_0",
        },
    ).tag({"sample", "sample_1", "mmle", "estimation"})

    all_pipes = s1_ns + auto_pred_ns + subsample_ns + mmle_ns

    return {
        "sample_s1": s1_ns,
        "auto_pred_s1": auto_pred_ns,
        "subsample_s1": subsample_ns,
        "mmle_estimation_s1": mmle_ns,
        "__default__": all_pipes,
    }
