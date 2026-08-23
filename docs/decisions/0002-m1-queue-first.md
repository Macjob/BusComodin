# ADR 0002 — Política queue-first para M1

## Estado

Aceptado para M1.

## Decisión

M1 agrega exactamente tres buses comodín al mismo escenario `synthetic-v1` y usa la misma demanda determinada por `seed` que M0. Los tres vehículos forman un **pool persistente durante toda la simulación**: no se consumen tras un único despacho.

Cada comodín parte desde uno de los hubs del escenario, distribuido de forma determinista. Cuando está disponible, la política observa las colas por combinación línea/paradero y selecciona la de mayor tamaño. El bus se reposiciona hasta ese paradero usando el camino más corto sobre el grafo sintético de paradas; ese tiempo se contabiliza antes de que pueda comenzar el servicio.

Una vez incorporado al servicio, el comodín continúa por el recorrido predefinido de la línea hasta su terminal. Al terminar, vuelve a quedar disponible desde ese terminal y puede ser reasignado a otra línea o tramo más adelante durante la misma jornada.

Los empates se resuelven determinísticamente por identificador de línea y posición del paradero. No se crean rutas libres ni se modifican demanda, capacidad, tiempos de viaje, líneas regulares o métricas de M0.

## Comparabilidad

`baseline` y `queue-first` llaman al mismo motor, generador de demanda y escenario. La única dimensión experimental modificada es la política de despacho y la existencia del pool de tres buses reutilizables.

Con seed 42, M0 y M1 generan ambos 808 pasajeros. El baseline registra 6.2131 minutos de espera media; queue-first persistente registra 5.8045 minutos. Los tres buses acumulan 10 asignaciones y 183 minutos de reposicionamiento en total. Este resultado es una observación de una sola semilla, no evidencia suficiente para concluir superioridad general; la evaluación multi-seed corresponde a M5.

## Consecuencias

- Los comodines pueden cambiar de servicio varias veces durante la jornada.
- No pueden teletransportarse: toda reasignación tiene costo temporal de reposicionamiento.
- El modelo ya permite medir asignaciones y tiempo total de reposicionamiento como base para métricas posteriores de utilización y kilómetros en vacío.
- La política `queue-first` sigue siendo deliberadamente simple: reacciona solo al tamaño de cola, sin umbrales ni información de espera acumulada o conectividad.

## Fuera de alcance

M1 no incorpora umbrales DTPM, tiempo acumulado de espera, vulnerabilidad de conectividad, datos reales ni optimización de parámetros.
