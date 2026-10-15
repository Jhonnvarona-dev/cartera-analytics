import pandas as pd
import pytest

from cartera.generador import generar_cartera
from cartera.priorizacion import priorizar_gestion

CORTE = pd.Timestamp("2026-10-01")


def cartera_ejemplo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id_obligacion": ["A", "B", "C"],
            "id_cliente": ["1", "2", "3"],
            "asesor": ["X", "X", "Y"],
            "saldo_inicial": [1000, 1000, 1000],
            "saldo_actual": [1000, 1000, 1000],
            "fecha_vencimiento": pd.to_datetime(
                ["2026-10-10", "2026-09-01", "2026-07-20"]
            ),
        }
    )
    # A: al día (peso 0) | B: 30 días (peso 1) | C: 73 días (peso 3)


def test_ordena_por_saldo_y_peso_del_rango():
    resultado = priorizar_gestion(cartera_ejemplo(), CORTE)
    assert list(resultado["id_obligacion"]) == ["C", "B"]


def test_excluye_obligaciones_al_dia():
    resultado = priorizar_gestion(cartera_ejemplo(), CORTE)
    assert "A" not in set(resultado["id_obligacion"])


def test_respeta_top_n():
    assert len(priorizar_gestion(cartera_ejemplo(), CORTE, top_n=1)) == 1


def test_top_n_invalido_falla():
    with pytest.raises(ValueError):
        priorizar_gestion(cartera_ejemplo(), CORTE, top_n=0)


def test_generador_es_reproducible_con_la_misma_semilla():
    pd.testing.assert_frame_equal(generar_cartera(50, semilla=1), generar_cartera(50, semilla=1))


def test_generador_produce_cartera_valida():
    df = generar_cartera(200)
    assert (df["saldo_actual"] <= df["saldo_inicial"]).all()
    assert (df["saldo_actual"] >= 0).all()
