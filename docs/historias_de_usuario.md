# Historias de usuario (criterios INVEST) y escenarios BDD

Cada historia es independiente, negociable, valiosa, estimable, pequeña y
verificable. Los escenarios en Gherkin están cubiertos por pruebas en `tests/`.

## HU-01 — Medir la morosidad de la cartera
**Como** coordinador de cobranza
**quiero** conocer el índice de morosidad a una fecha de corte
**para** saber qué parte del saldo está vencida.

```gherkin
Escenario: Cálculo del índice de morosidad
  Dado una cartera con saldo pendiente total de 2000
  Y obligaciones vencidas con saldo pendiente de 1000
  Cuando calculo el índice de morosidad a la fecha de corte
  Entonces el resultado es 50%

Escenario: Cartera sin saldo pendiente
  Dado una cartera cuyo saldo pendiente es 0
  Cuando calculo el índice de morosidad
  Entonces el resultado es 0%
```
Pruebas: `test_indice_morosidad`, `test_indice_morosidad_sin_saldo_es_cero`.

## HU-02 — Clasificar obligaciones por rango de mora
**Como** asesor de cartera
**quiero** ver cada obligación clasificada en un rango de mora
**para** definir la estrategia de contacto.

```gherkin
Esquema del escenario: Rangos de mora
  Dado una obligación con <dias> días de mora
  Cuando la clasifico
  Entonces su rango es "<rango>"

  Ejemplos:
    | dias | rango |
    | 0    | Al día |
    | 30   | 1-30   |
    | 31   | 31-60  |
    | 91   | +90    |
```
Pruebas: `test_rango_mora_limites`.

## HU-03 — Priorizar la gestión de cobro
**Como** asesor de cartera
**quiero** una lista ordenada de las obligaciones que debo gestionar primero
**para** aprovechar mejor mi tiempo.

```gherkin
Escenario: Orden de prioridad
  Dado obligaciones con el mismo saldo en distintos rangos de mora
  Cuando solicito la lista de prioridad
  Entonces las de mayor peso aparecen primero
  Y las obligaciones al día no aparecen
```
Pruebas: `test_ordena_por_saldo_y_peso_del_rango`, `test_excluye_obligaciones_al_dia`.

## Planeación de pruebas (Test Planning)
| Nivel | Qué se prueba | Dónde |
|---|---|---|
| Unitarias | Funciones de métricas, rangos y validaciones | `tests/test_metricas.py` |
| Integración ligera | Generador + priorización con datos sintéticos | `tests/test_priorizacion.py` |
| Calidad en CI | Todas las pruebas se ejecutan en cada push | `.github/workflows/ci.yml` |
