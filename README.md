# Cartera Analytics

![CI](https://github.com/Jhonnvarona-dev/cartera-analytics/actions/workflows/ci.yml/badge.svg)

Herramienta en Python para analizar una cartera de cobro: **mora por rangos, índice de morosidad, tasa de recaudo, desempeño por asesor y priorización de la gestión**.

Nació de un caso que conozco de primera mano: más de 9 años trabajando en recuperación de cartera. Quise convertir las métricas que uso a diario en código probado y reproducible.

> **Los datos son 100% sintéticos** (los genera `generador.py`). No contiene información real de clientes ni de empresas.

## Qué incluye
- **Métricas de cartera** (`src/cartera/metricas.py`): días y rango de mora, índice de morosidad, tasa de recaudo, resúmenes por rango y por asesor, y validación de datos.
- **Priorización de gestión** (`src/cartera/priorizacion.py`): ordena obligaciones por `saldo × peso del rango de mora`. Los pesos son un supuesto de negocio configurable.
- **Generador de datos ficticios** reproducible con semilla.
- **Pruebas automatizadas** con pytest (unitarias y de integración ligera).
- **Historias de usuario (INVEST) y escenarios BDD/Gherkin** en `docs/historias_de_usuario.md`.
- **CI con GitHub Actions**: las pruebas corren en cada push.

## Cómo ejecutarlo
```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest -v                        # correr las pruebas
PYTHONPATH=src python -m cartera.reporte   # reporte de ejemplo (Windows: set PYTHONPATH=src)
```
El reporte imprime las métricas y guarda `output/prioridad_gestion.csv`.

## Definiciones
| Métrica | Fórmula |
|---|---|
| Días de mora | `max(0, fecha_corte − fecha_vencimiento)` |
| Índice de morosidad | saldo pendiente vencido / saldo pendiente total |
| Tasa de recaudo | (saldo inicial − saldo actual) / saldo inicial |

## Estructura
```
src/cartera/     código (métricas, priorización, generador, reporte)
tests/           pruebas con pytest
docs/            historias de usuario y plan de pruebas
.github/         pipeline de CI
```

## Próximos pasos
- Dashboard en Power BI o Streamlit con los resultados.
- Modelo de probabilidad de pago con Scikit-Learn.
- Pruebas de propiedades y mayor cobertura.
