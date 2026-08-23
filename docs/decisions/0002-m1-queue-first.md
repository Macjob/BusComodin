# ADR 0002 — Política queue-first para M1

## Estado

Aceptado para M1.

## Decisión

M1 agrega exactamente tres buses comodín al mismo escenario `synthetic-v1` y usa la misma demanda determinada por `seed` que M0. En cada minuto, mientras queden comodines sin despachar, la política observa las colas por combinación línea/paradero y selecciona la de mayor tamaño.

El refuerzo se inserta en ese paradero y continúa por el recorrido predefinido de la línea hasta su término. No crea rutas libres ni modifica demanda, capacidad, tiempos de viaje, líneas regulares o métricas.

Los empates se resuelven determinísticamente por identificador de línea y posición del paradero. Cada uno de los tres comodines se despacha una sola vez durante la corrida.

## Comparabilidad

`baseline` y `queue-first` llaman al mismo motor, generador de demanda y escenario. La única dimensión experimental modificada es la política de despacho y la disponibilidad de tres buses de refuerzo.

Con seed 42, M0 y M1 generan ambos 808 pasajeros. El baseline registra 6.2131 minutos de espera media y queue-first 5.9798 minutos. Este resultado es una observación de una sola semilla, no evidencia suficiente para concluir superioridad general; la evaluación multi-seed corresponde a M5.

## Fuera de alcance

M1 no incorpora umbrales DTPM, tiempo acumulado de espera, vulnerabilidad de conectividad, datos reales ni optimización de parámetros.
