from kedro.pipeline import Pipeline, node

from .nodes import plot_mmle_summary, plot_bayes_summary, plot_bayes_vs_mmle_baselines


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        node(
            func=plot_mmle_summary,
            inputs={"mmle_summary": "mmle_estimation__s1.mmle_estimation_summary"},
            outputs={
                # Use local names; pipeline namespace will prefix to reporting__s1.*
                "mmle_fig_percent_vs_mse": "mmle_fig_percent_vs_mse",
                "mmle_fig_percent_vs_r2": "mmle_fig_percent_vs_r2",
            },
            name="s1_plot_mmle_summary",
            tags={"sample_1", "reporting", "mmle"},
        ),
        node(
            func=plot_bayes_summary,
            inputs={"bayes_summary": "bayes_estimation__s1.bayes_estimation_summary"},
            outputs={
                # Use local names; pipeline namespace will prefix to reporting__s1.*
                "bayes_fig_percent_vs_mse": "bayes_fig_percent_vs_mse",
                "bayes_fig_percent_vs_r2": "bayes_fig_percent_vs_r2",
            },
            name="s1_plot_bayes_summary",
            tags={"sample_1", "reporting", "bayes"},
        ),
        node(
            func=plot_bayes_vs_mmle_baselines,
            inputs={
                "mmle_summary": "mmle_estimation__s1.mmle_estimation_summary",
                "bayes_summary": "bayes_estimation__s1.bayes_estimation_summary",
            },
            outputs={
                "bayes_r2_with_mmle_hlines": "bayes_r2_with_mmle_hlines",
                "bayes_mse_with_mmle_hlines": "bayes_mse_with_mmle_hlines",
            },
            name="s1_plot_bayes_vs_mmle_baselines",
            tags={"sample_1", "reporting", "comparison"},
        ),
    ]
    return Pipeline(nodes)
