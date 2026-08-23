# M7 — Hallazgos PER0002 y fuentes operacionales

## Estado

Investigación en curso. Este documento registra qué datos operacionales oficiales se localizaron y cómo se usarán sin inferir parámetros innecesariamente.

## PER0002 — Gran Valparaíso (2025–2026)

El portal oficial DTPR mantiene la licitación PER0002 del Gran Valparaíso, publicada el 01-07-2025. El expediente contiene, entre otros:

- Condiciones de Operación del Perímetro de Exclusión.
- Bases Técnicas y Administrativas.
- Informe Técnico de Transporte Público de Gran Valparaíso.
- modificaciones, respuestas a consultas y antecedentes de evaluación/adjudicación.

Landing page versionada en el manifest M7:

`https://dtpr.mtt.gob.cl/consultalicitaciones/webpage/Licitaciones.aspx?id=10464`

El proceso ya contiene antecedentes posteriores a la licitación original, incluyendo evaluación y adjudicación durante 2026. Por lo tanto, para parámetros operacionales se debe preferir la versión vigente/modificada del expediente sobre documentos anteriores cuando exista contradicción.

## Informe Técnico Gran Valparaíso

Se localizó un Informe Técnico oficial del DTPR asociado al expediente. Entre los antecedentes operacionales reporta comparación entre expediciones exigidas y observadas para agosto 2022–julio 2023 y señala deterioro del cumplimiento de frecuencias a lo largo del día. El documento constituye una fuente útil para modelar irregularidad operacional real, no solo frecuencias nominales.

No se copiarán cifras a la configuración del simulador hasta identificar su unidad de negocio/servicio y periodo exactos.

## Programas operacionales DTPR

DTPR mantiene un buscador oficial de programas operacionales `PO / POT / POR` por zona regulada:

`https://dtpr.mtt.gob.cl/EEX/WebPage/PublicacionesProgramas.aspx`

Esta fuente es prioritaria para obtener oferta programada/frecuencias vigentes antes de estimarlas.

### Corrección de vigencia importante

La investigación encontró que 120/122/125 son una referencia histórica útil, pero **no deben ser el objetivo operacional vigente de M7**. El contrato oficial UN11 aprobado por Decreto Exento N°792/2025 asigna los servicios `C01`, `C02`, `C03`, `C03Y` y `C04` en Quilpué/Villa Alemana, y señala que sus trazados están definidos por el Programa de Operación (Anexo N°3) de las bases del concurso regulado por Decreto Exento N°4515/2024.

El portal DTPR del concurso `DSL4654 - UN11`, publicado el 22-10-2024, ofrece además un **KMZ Servicios UN11** y las Bases de Licitación. Por tanto, M7 debe pivotar a C01/C02/C03/C03Y/C04 para el escenario vigente, conservando 120/122/125 solo como antecedente 2022 y como caso histórico comparable.

También se materializó localmente el Decreto Afecto N°79/2021 de ELC0004. Su Anexo N°1 confirma que el programa antiguo sí contenía frecuencias horarias explícitas; por ejemplo, el servicio 120 tenía tablas por hora y tipo de día. Esto valida la estrategia de extraer frecuencia directamente de programas oficiales, pero esos valores no se usarán como si fueran vigentes en 2026.

## Manuales operacionales históricos aún relevantes

El expediente ELC0004 enlaza documentos regulatorios generales que pueden ayudar a interpretar los programas:

- Resolución Exenta 1413/2018: Manual de Condiciones Técnicas de Establecimiento y Modificaciones de los Programas de Operación.
- Resolución Exenta 2876/2018: tratamiento de indicadores de cumplimiento (visible en expedientes relacionados).
- Resolución Exenta 1247/2015: estándares técnicos de sistemas AVL.

Estos documentos sirven para interpretar estructura/indicadores; no reemplazan un programa operacional vigente.

## Recaudación electrónica REC0006 (2025)

Existe además una licitación oficial para recaudación electrónica que cubre Valparaíso, Viña del Mar, Concón, Quilpué y Villa Alemana. Es potencialmente relevante a futuro para entender la disponibilidad de validaciones/afluencia, pero no se asumirá que sus datos transaccionales sean públicos ni accesibles para M7.

## Regla de decisión para M7

1. **Trazado:** para el escenario vigente, priorizar KMZ oficial UN11 2024 de C01/C02/C03/C03Y/C04; mantener el KMZ 120/122/125 de 2022 como referencia histórica versionada.
2. **Frecuencia/oferta:** programa operacional oficial vigente de UN11 (Anexo N°3 / PO-POT-POR) si se logra materializar; PER0002 como contexto del sistema mayor.
3. **Irregularidad:** informe técnico/indicadores observados, manteniendo periodo y alcance explícitos.
4. **Paradas:** fuente oficial moderna si se localiza; de lo contrario, fuente pública secundaria claramente etiquetada. No deducir paradas desde vértices del shape.
5. **Demanda:** EOD SECTRA histórica como calibración separada; no confundir con demanda 2026.
6. **AVL/GPS:** usar solo si aparece dataset público; los estándares AVL prueban existencia del sistema, no disponibilidad de sus datos.

## Próxima acción

Materializar desde `DSL4654 - UN11` el KMZ 2024 y las Bases del Decreto Exento N°4515/2024. Extraer C01/C02/C03/C03Y/C04, sus frecuencias y condiciones operacionales del Anexo N°3, registrando checksum + provenance de la misma forma usada para el KMZ histórico. Luego localizar paradas modernas antes de construir `scenario-villa-alemana-real-v1`.
