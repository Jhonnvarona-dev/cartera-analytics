"""Métricas de cartera.

Las funciones son puras (no modifican el DataFrame original) para que sean
fáciles de probar.

Columnas esperadas en el DataFrame de cartera:
    id_obligacion, id_cliente, asesor,
    saldo_inicial, saldo_actual (en COP),
    fecha_vencimiento (datetime)
"""
from __future__ import annotations

import pandas as pd

COLUMNAS_REQUERIDAS = [
    "id_obligacion",
    "id_cliente",
    "asesor",
    "saldo_inicial",
    "saldo_actual",
    "fecha_vencimiento",
]

# Orden en el que se muestran los rangos de mora.
RANGOS = ["Al día", "1-30", "31-60", "61-90", "+90"]


def validar_cartera(df: pd.DataFrame) -> None:
    """Lanza ValueError si la cartera tiene columnas faltantes o saldos inválidos."""
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")
    if (df["saldo_inicial"] <= 0).any():
        raise ValueError("saldo_inicial debe ser mayor a cero")
    if (df["saldo_actual"] < 0).any():
        raise ValueError("saldo_actual no puede ser negativo")
    if (df["saldo_actual"] > df["saldo_inicial"]).any():
        raise ValueError("saldo_actual no puede superar el saldo_inicial")


def dias_mora(fecha_vencimiento: pd.Timestamp, fecha_corte: pd.Timestamp) -> int:
    """Días de mora a la fecha de corte. Si aún no vence, retorna 0."""
    dias = (pd.Timestamp(fecha_corte) - pd.Timestamp(fecha_vencimiento)).days
    return max(0, dias)


def rango_mora(dias: int) -> str:
    """Clasifica los días de mora en un rango."""
    if dias < 0:
        raise ValueError("Los días de mora no pueden ser negativos")
    if dias == 0:
        return "Al día"
    if dias <= 30:
        return "1-30"
    if dias <= 60:
        return "31-60"
    if dias <= 90:
        return "61-90"
    return "+90"


def agregar_mora(df: pd.DataFrame, fecha_corte: pd.Timestamp) -> pd.DataFrame:
    """Devuelve una copia del DataFrame con las columnas dias_mora y rango_mora."""
    validar_cartera(df)
    resultado = df.copy()
    resultado["dias_mora"] = resultado["fecha_vencimiento"].apply(
        lambda f: dias_mora(f, fecha_corte)
    )
    resultado["rango_mora"] = resultado["dias_mora"].apply(rango_mora)
    return resultado


def indice_morosidad(df: pd.DataFrame, fecha_corte: pd.Timestamp) -> float:
    """Saldo en mora / saldo total vigente (entre 0 y 1).

    Solo cuenta el saldo pendiente: una obligación pagada no aporta.
    """
    datos = agregar_mora(df, fecha_corte)
    saldo_total = datos["saldo_actual"].sum()
    if saldo_total == 0:
        return 0.0
    saldo_en_mora = datos.loc[datos["dias_mora"] > 0, "saldo_actual"].sum()
    return float(saldo_en_mora / saldo_total)


def tasa_recaudo(df: pd.DataFrame) -> float:
    """Porcentaje recuperado del saldo inicial (entre 0 y 1)."""
    validar_cartera(df)
    inicial = df["saldo_inicial"].sum()
    recaudado = inicial - df["saldo_actual"].sum()
    return float(recaudado / inicial)


def resumen_por_rango(df: pd.DataFrame, fecha_corte: pd.Timestamp) -> pd.DataFrame:
    """Número de obligaciones y saldo pendiente por rango de mora."""
    datos = agregar_mora(df, fecha_corte)
    resumen = (
        datos.groupby("rango_mora")
        .agg(obligaciones=("id_obligacion", "count"), saldo=("saldo_actual", "sum"))
        .reindex(RANGOS, fill_value=0)
    )
    resumen.index.name = "rango_mora"
    return resumen


def resumen_por_asesor(df: pd.DataFrame) -> pd.DataFrame:
    """Tasa de recaudo y saldo pendiente por asesor, de mayor a menor recaudo."""
    validar_cartera(df)
    por_asesor = df.groupby("asesor").agg(
        saldo_inicial=("saldo_inicial", "sum"),
        saldo_actual=("saldo_actual", "sum"),
    )
    por_asesor["tasa_recaudo"] = (
        por_asesor["saldo_inicial"] - por_asesor["saldo_actual"]
    ) / por_asesor["saldo_inicial"]
    return por_asesor.sort_values("tasa_recaudo", ascending=False)
