import pandas as pd
import pytest

from cartera.metricas import (
    agregar_mora,
    dias_mora,
    indice_morosidad,
    rango_mora,
    resumen_por_asesor,
    resumen_por_rango,
    tasa_recaudo,
    validar_cartera,
)

CORTE = pd.Timestamp("2026-10-01")


def cartera_ejemplo() -> pd.DataFrame:
    """Cuatro obligaciones con resultados fáciles de calcular a mano."""
    return pd.DataFrame(
        {
            "id_obligacion": ["A", "B", "C", "D"],
            "id_cliente": ["1", "2", "3", "4"],
            "asesor": ["X", "X", "Y", "Y"],
            "saldo_inicial": [1000, 1000, 1000, 1000],
            "saldo_actual": [1000, 500, 0, 500],
            "fecha_vencimiento": pd.to_datetime(
                ["2026-10-10", "2026-09-01", "2026-06-01", "2026-07-01"]
            ),
        }
    )
    # A: aún no vence (al día) | B: 30 días | C: pagada (+90) | D: 92 días


def test_dias_mora_no_vencida_es_cero():
    assert dias_mora(pd.Timestamp("2026-10-10"), CORTE) == 0


def test_dias_mora_vencida():
    assert dias_mora(pd.Timestamp("2026-09-01"), CORTE) == 30


@pytest.mark.parametrize(
    "dias, esperado",
    [(0, "Al día"), (1, "1-30"), (30, "1-30"), (31, "31-60"), (60, "31-60"),
     (61, "61-90"), (90, "61-90"), (91, "+90"), (400, "+90")],
)
def test_rango_mora_limites(dias, esperado):
    assert rango_mora(dias) == esperado


def test_rango_mora_negativo_falla():
    with pytest.raises(ValueError):
        rango_mora(-1)


def test_indice_morosidad():
    # Saldo total = 1000 + 500 + 0 + 500 = 2000; en mora = 500 (B) + 500 (D) = 1000
    assert indice_morosidad(cartera_ejemplo(), CORTE) == pytest.approx(0.5)


def test_indice_morosidad_sin_saldo_es_cero():
    df = cartera_ejemplo()
    df["saldo_actual"] = 0
    assert indice_morosidad(df, CORTE) == 0.0


def test_tasa_recaudo():
    # Recaudado = 4000 - 2000 = 2000 sobre 4000
    assert tasa_recaudo(cartera_ejemplo()) == pytest.approx(0.5)


def test_agregar_mora_no_modifica_el_original():
    df = cartera_ejemplo()
    agregar_mora(df, CORTE)
    assert "dias_mora" not in df.columns


def test_resumen_por_rango_incluye_todos_los_rangos():
    resumen = resumen_por_rango(cartera_ejemplo(), CORTE)
    assert list(resumen.index) == ["Al día", "1-30", "31-60", "61-90", "+90"]
    assert resumen.loc["1-30", "saldo"] == 500
    assert resumen.loc["+90", "obligaciones"] == 2
    assert resumen.loc["31-60", "obligaciones"] == 0


def test_resumen_por_asesor_ordena_por_recaudo():
    resumen = resumen_por_asesor(cartera_ejemplo())
    # X recaudó 500/2000 = 0.25 ; Y recaudó 1500/2000 = 0.75
    assert list(resumen.index) == ["Y", "X"]
    assert resumen.loc["Y", "tasa_recaudo"] == pytest.approx(0.75)


def test_validar_columnas_faltantes():
    with pytest.raises(ValueError, match="Faltan columnas"):
        validar_cartera(cartera_ejemplo().drop(columns=["asesor"]))


def test_validar_saldo_actual_mayor_al_inicial():
    df = cartera_ejemplo()
    df.loc[0, "saldo_actual"] = 2000
    with pytest.raises(ValueError, match="superar"):
        validar_cartera(df)


def test_validar_saldo_negativo():
    df = cartera_ejemplo()
    df.loc[0, "saldo_actual"] = -1
    with pytest.raises(ValueError, match="negativo"):
        validar_cartera(df)
