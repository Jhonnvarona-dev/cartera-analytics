"""Genera un reporte de ejemplo.  Uso:  python -m cartera.reporte"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from cartera.generador import generar_cartera
from cartera.metricas import (
    indice_morosidad,
    resumen_por_asesor,
    resumen_por_rango,
    tasa_recaudo,
)
from cartera.priorizacion import priorizar_gestion


def main(salida: str = "output") -> None:
    corte = pd.Timestamp("2026-10-01")
    cartera = generar_cartera(fecha_corte=str(corte.date()))

    print(f"Fecha de corte: {corte.date()}  |  Obligaciones: {len(cartera)}")
    print(f"Índice de morosidad: {indice_morosidad(cartera, corte):.1%}")
    print(f"Tasa de recaudo:     {tasa_recaudo(cartera):.1%}\n")
    print("Resumen por rango de mora:")
    print(resumen_por_rango(cartera, corte).to_string(), "\n")
    print("Resumen por asesor:")
    print(resumen_por_asesor(cartera).round(3).to_string())

    carpeta = Path(salida)
    carpeta.mkdir(exist_ok=True)
    priorizar_gestion(cartera, corte, top_n=20).to_csv(
        carpeta / "prioridad_gestion.csv", index=False
    )
    print(f"\nArchivo generado: {carpeta / 'prioridad_gestion.csv'}")


if __name__ == "__main__":
    main()
