"""Genera datos SINTÉTICOS de cartera (no contienen información real)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def generar_cartera(
    n: int = 500, fecha_corte: str = "2026-10-01", semilla: int = 42
) -> pd.DataFrame:
    """Crea una cartera ficticia reproducible (misma semilla = mismos datos)."""
    if n <= 0:
        raise ValueError("n debe ser mayor a cero")
    rng = np.random.default_rng(semilla)
    corte = pd.Timestamp(fecha_corte)

    saldo_inicial = (rng.lognormal(mean=14.5, sigma=0.6, size=n) // 1000 * 1000)
    saldo_inicial = np.clip(saldo_inicial, 100_000, None)

    # La mitad no ha pagado nada; el resto pagó entre 10% y 100%.
    pago = np.where(rng.random(n) < 0.5, 0.0, rng.uniform(0.1, 1.0, size=n))
    saldo_actual = (saldo_inicial * (1 - pago) // 1000 * 1000)

    # Vencimientos entre 60 días a futuro y 120 días atrás.
    desfase = rng.integers(-60, 121, size=n)
    vencimiento = corte - pd.to_timedelta(desfase, unit="D")

    return pd.DataFrame(
        {
            "id_obligacion": [f"OB-{i:05d}" for i in range(1, n + 1)],
            "id_cliente": [f"CL-{rng.integers(1, n // 2 + 2):05d}" for _ in range(n)],
            "asesor": rng.choice(["Asesor A", "Asesor B", "Asesor C", "Asesor D"], size=n),
            "saldo_inicial": saldo_inicial,
            "saldo_actual": saldo_actual,
            "fecha_vencimiento": vencimiento,
        }
    )
