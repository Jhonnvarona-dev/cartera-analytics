"""Priorización de la gestión de cobro.

SUPUESTO DE NEGOCIO (configurable): los pesos por rango son una regla simple
de ejemplo. Entre 31 y 90 días la gestión suele ser más efectiva que en
rangos muy avanzados, por eso pesan más. Ajústalos a tu operación.
"""
from __future__ import annotations

import pandas as pd

from cartera.metricas import agregar_mora

PESOS_POR_RANGO = {
    "Al día": 0.0,  # no requiere gestión de cobro
    "1-30": 1.0,
    "31-60": 2.0,
    "61-90": 3.0,
    "+90": 1.5,
}


def priorizar_gestion(
    df: pd.DataFrame,
    fecha_corte: pd.Timestamp,
    top_n: int = 10,
    pesos: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Ordena las obligaciones por prioridad = saldo_actual * peso del rango."""
    if top_n <= 0:
        raise ValueError("top_n debe ser mayor a cero")
    pesos = pesos or PESOS_POR_RANGO
    datos = agregar_mora(df, fecha_corte)
    datos["prioridad"] = datos["saldo_actual"] * datos["rango_mora"].map(pesos)
    datos = datos[datos["prioridad"] > 0]
    return datos.sort_values("prioridad", ascending=False).head(top_n)
