## Estrategia de ramas (Git flow sencillo)

| Rama                       | Propósito                                              |
| -------------------------- | ------------------------------------------------------ |
| `main`                     | Producción; CI pasa y GitHub Pages se actualiza        |
| `dev`                      | Integración continua de nuevas features                |
| `feature/sim-params`       | Nodo 1 – simulación de `theta` y `b_true`              |
| `feature/pred-b-prior`     | Nodo 2 – generación de `b_pred` con \$R^{2}\$ variable |
| `feature/sim-responses`    | Nodo 3 – creación de la matriz de respuestas           |
| `feature/mle-estimation`   | Nodo 4 – estimación clásica                            |
| `feature/bayes-estimation` | Nodo 5 – modelo PyMC                                   |
| `feature/comparison`       | Nodo 6 – métricas + figuras                            |
| `feature/report`           | Nodo 7 – exporte JSON / MLflow & resumen Markdown      |
| `ci/kedro-action`          | GitHub Action de ejecución automática                  |
| `docs/gh-pages`            | Fuente de la web (se publica a `gh-pages`)             |

