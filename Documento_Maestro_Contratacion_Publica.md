# Documento Maestro del Proyecto

Sistema de Recolección de Datos de Contratación Pública

Especificación de Requerimientos (SRS) y Arquitectura de Software

Versión 1.0

*Estándares de referencia: IEEE 830-1998 / ISO·IEC·IEEE 29148*

Fecha: 19 de junio de 2026

# Contenido

# Parte I — Especificación de Requerimientos de Software (SRS)

- 1. Introducción

- 2. Descripción General del Sistema

- 3. Requerimientos Funcionales

- 4. Requerimientos No Funcionales

- 5. Historias de Usuario

- 6. Modelo de Datos y Arquitectura (vista lógica)

- 7. Criterios de Aceptación

- 8. Trazabilidad (qué demuestra el proyecto)

# Parte II — Documento de Arquitectura de Software

- 9. Introducción a la Arquitectura

- 10. Necesidades de Arquitectura

- 11. Estilo Arquitectónico Seleccionado

- 12. Arquitectura de Componentes

- 13. Vista de Despliegue

- 14. Tácticas de Diseño por Atributo de Calidad

- 15. Riesgos Arquitectónicos y Mitigaciones

- 16. Plan de Desarrollo por Fases (Desarrollador Único)

# Parte I — Especificación de Requerimientos de Software (SRS)

# 1. Introducción

## 1.1 Propósito

Este documento especifica los requerimientos funcionales y no funcionales del Sistema de Recolección de Datos de Contratación Pública, un pipeline de extracción, transformación y carga (ETL) que consolida información de contratación gubernamental dispersa en múltiples fuentes y formatos en una única base de datos analizable. El documento sigue la estructura propuesta por el SDLC (Software Development Life Cycle) en su fase de Análisis de Requerimientos, y se apoya en los lineamientos del estándar IEEE 830 para la redacción del SRS.

## 1.2 Alcance

El sistema cubrirá las etapas de extracción de datos desde fuentes públicas (SECOP Colombia, Datos Abiertos Colombia y otras fuentes de contratos públicos), normalización y validación de la información, carga en una base de datos PostgreSQL, y visualización mediante un dashboard. El despliegue se apoyará en Docker y la automatización del pipeline en GitHub Actions. Quedan fuera de alcance la negociación o gestión de contratos, así como cualquier funcionalidad transaccional sobre los datos de origen.

## 1.3 Definiciones, acrónimos y abreviaturas

| **Término** | **Definición** |
| --- | --- |
| SECOP | Sistema Electrónico de Contratación Pública de Colombia. |
| ETL | Extract, Transform, Load: proceso de extracción, transformación y carga de datos. |
| SRS | Software Requirements Specification (Especificación de Requerimientos de Software). |
| RF | Requerimiento Funcional. |
| RNF | Requerimiento No Funcional. |
| HU | Historia de Usuario. |
| SDLC | Software Development Life Cycle (Ciclo de Vida de Desarrollo de Software). |

## 1.4 Referencias

- IEEE Std 830-1998: Recommended Practice for Software Requirements Specifications.

- ISO/IEC/IEEE 29148:2018: Systems and software engineering, Life cycle processes, Requirements engineering.

- Portal de Datos Abiertos de Colombia (datos.gov.co).

- SECOP: Sistema Electronico de Contratacion Publica (colombiacompra.gov.co).

## 1.5 Visión general del documento

El documento se organiza siguiendo las fases del SDLC relevantes a la etapa de requerimientos en su Parte I, y a la etapa de diseño arquitectónico en su Parte II: descripción general del sistema, requerimientos funcionales, requerimientos no funcionales, historias de usuario, modelo de datos, arquitectura propuesta y criterios de aceptación.

# 2. Descripción General del Sistema

## 2.1 Problema a resolver

Las entidades gubernamentales publican contratos en diferentes formatos y fuentes, lo que dificulta su análisis conjunto. Se requiere consolidar esta información dispersa en una única base de datos estructurada que permita análisis confiable y comparativo.

## 2.2 Perspectiva del producto

El sistema es un pipeline de datos compuesto por módulos independientes de extracción, normalización, validación, carga y visualización. No depende de sistemas externos distintos a las fuentes públicas de datos y la infraestructura de base de datos y orquestación definida por el propio proyecto.

## 2.3 Funciones principales

- Extracción automatizada de contratos públicos mediante scraping (Requests + BeautifulSoup).

- Normalización de entidades y campos con nomenclatura inconsistente.

- Validación de reglas de calidad de datos antes de la carga.

- Carga estructurada en PostgreSQL (tablas contracts, entities, suppliers).

- Visualización de los datos consolidados mediante un dashboard.

- Orquestación y automatización del pipeline mediante GitHub Actions.

- Empaquetado y despliegue reproducible mediante Docker.

## 2.4 Usuarios y características

| **Usuario** | **Descripción** |
| --- | --- |
| Analista de datos / contratación | Consume los datos consolidados y el dashboard para análisis de contratación pública. |
| Desarrollador / mantenedor | Opera y extiende el pipeline ETL, gestiona el despliegue y la automatización. |
| Reclutador / evaluador técnico | Revisa el proyecto como evidencia de habilidades técnicas (scraping, ETL, calidad de datos, arquitectura). |

## 2.5 Restricciones

- El sistema debe construirse con el stack tecnológico definido: Python, Requests, BeautifulSoup, Pandas, PostgreSQL, SQLAlchemy, Docker y GitHub Actions.

- El acceso a las fuentes públicas depende de la disponibilidad y estructura HTML/API de los portales gubernamentales, que pueden cambiar sin previo aviso.

- El sistema no tiene control sobre la calidad de los datos en el origen; solo puede detectar y rechazar inconsistencias.

## 2.6 Supuestos y dependencias

- Se asume que las fuentes públicas (SECOP, Datos Abiertos Colombia) permanecen accesibles públicamente durante el desarrollo y operación del sistema.

- Se asume disponibilidad de un servidor o contenedor con PostgreSQL accesible desde el proceso ETL.

- Se asume que GitHub Actions tendrá acceso a las credenciales necesarias mediante secretos configurados en el repositorio.

# 3. Requerimientos Funcionales

A continuación se listan los requerimientos funcionales (RF) identificados a partir del alcance del proyecto, organizados por las etapas del pipeline: extracción, transformación, carga y visualización.

| **ID** | **Descripción** | **Prioridad** |
| --- | --- | --- |
| RF-01 | El sistema debe extraer datos de contratación pública desde fuentes como SECOP Colombia y Datos Abiertos Colombia mediante scraping en Python. | Alta |
| RF-02 | El extractor debe capturar como mínimo: entidad, contratista, valor, fecha y estado del contrato. | Alta |
| RF-03 | El sistema debe normalizar nombres de entidades equivalentes (ej. “Ministerio TIC”, “MIN TIC”, “MinTIC”) a una forma canónica única. | Alta |
| RF-04 | El sistema debe validar que el valor del contrato sea mayor a cero antes de cargarlo a la base de datos. | Alta |
| RF-05 | El sistema debe validar que la fecha del contrato no sea nula antes de cargarlo a la base de datos. | Alta |
| RF-06 | Los registros que no superen las validaciones deben ser rechazados y registrados en un log de errores, sin detener el pipeline. | Media |
| RF-07 | El sistema debe cargar los datos transformados en las tablas contracts, entities y suppliers de PostgreSQL. | Alta |
| RF-08 | El sistema debe evitar la duplicación de registros ya existentes en la base de datos (idempotencia de carga). | Media |
| RF-09 | El sistema debe exponer los datos consolidados a través de un dashboard de visualización. | Alta |
| RF-10 | El dashboard debe permitir filtrar contratos por entidad, contratista, rango de fechas y estado. | Media |
| RF-11 | El pipeline completo (extracción, transformación, carga) debe poder ejecutarse de forma automatizada mediante GitHub Actions. | Media |
| RF-12 | El sistema debe poder desplegarse mediante contenedores Docker para garantizar reproducibilidad del entorno. | Media |

# 4. Requerimientos No Funcionales

Los requerimientos no funcionales (RNF) describen atributos de calidad que el sistema debe cumplir, independientemente de su funcionalidad específica.

| **ID** | **Categoría** | **Descripción** |
| --- | --- | --- |
| RNF-01 | Confiabilidad | El proceso ETL debe registrar logs detallados de ejecución para permitir auditoría y depuración de fallos. |
| RNF-02 | Disponibilidad | El dashboard debe estar disponible para consulta con un tiempo de actividad razonable durante horario laboral. |
| RNF-03 | Mantenibilidad | El código debe organizarse en módulos independientes (extract, transform, load) siguiendo el principio de responsabilidad única. |
| RNF-04 | Portabilidad | El sistema debe ejecutarse de forma idéntica en distintos entornos mediante Docker. |
| RNF-05 | Escalabilidad | El esquema de base de datos debe soportar el crecimiento del volumen de contratos sin degradar el rendimiento de las consultas. |
| RNF-06 | Calidad de datos | El proceso de validación debe rechazar registros inconsistentes antes de su persistencia, garantizando integridad referencial. |
| RNF-07 | Seguridad | Las credenciales de base de datos y servicios externos deben gestionarse mediante variables de entorno o secretos, nunca en código fuente. |
| RNF-08 | Usabilidad | El dashboard debe presentar la información de forma clara para un usuario no técnico (reclutador o analista). |
| RNF-09 | Rendimiento | El proceso de scraping y carga debe completarse en un tiempo razonable acorde al volumen de fuentes configuradas. |
| RNF-10 | Trazabilidad | Cada registro cargado debe conservar su fuente de origen para permitir trazabilidad del dato. |

# 5. Historias de Usuario

Las historias de usuario (HU) complementan los requerimientos funcionales expresando la necesidad desde la perspectiva de cada rol involucrado, siguiendo el formato “Como [rol], quiero [acción], para [beneficio]”.

| **ID** | **Historia de usuario** | **Prioridad** |
| --- | --- | --- |
| HU-01 | Como analista de datos, quiero que el sistema extraiga automáticamente contratos publicados en SECOP, para no tener que recopilarlos manualmente. | Alta |
| HU-02 | Como analista de datos, quiero que los nombres de entidades se normalicen, para poder agrupar y comparar contratos de una misma entidad sin duplicados por nombre. | Alta |
| HU-03 | Como administrador del sistema, quiero que los registros inválidos se rechacen y queden registrados en un log, para garantizar la calidad de los datos sin perder visibilidad de los errores. | Media |
| HU-04 | Como reclutador o evaluador técnico, quiero visualizar un dashboard con los contratos consolidados, para entender rápidamente el alcance y la calidad del proyecto. | Media |
| HU-05 | Como desarrollador del proyecto, quiero que el pipeline se ejecute automáticamente mediante GitHub Actions, para no tener que correr cada etapa manualmente. | Baja |
| HU-06 | Como desarrollador del proyecto, quiero desplegar el sistema con Docker, para asegurar que funcione igual en cualquier máquina. | Baja |

# 6. Modelo de Datos y Arquitectura (vista lógica)

## 6.1 Arquitectura del pipeline

El sistema sigue una arquitectura de pipeline lineal con las siguientes etapas:

*Fuentes Públicas → Scraper Python → Normalización → PostgreSQL → Dashboard*

## 6.2 Estructura de extracción (src/extract/)

El módulo de extracción es responsable de obtener, por cada contrato publicado, como mínimo los siguientes campos:

- Entidad

- Contratista

- Valor

- Fecha

- Estado

## 6.3 Reglas de transformación

Normalización de nombres de entidades equivalentes a una forma canónica. Ejemplo:

| **Variantes en origen** | **Forma canónica** |
| --- | --- |
| Ministerio TIC / MIN TIC / MinTIC | Ministerio de Tecnologías de la Información y las Comunicaciones |

## 6.4 Reglas de validación

Antes de la carga, cada registro debe pasar las siguientes validaciones mínimas:

- assert valor > 0

- assert fecha is not None

## 6.5 Modelo de carga (PostgreSQL)

Los datos validados se persisten en las siguientes tablas principales (el detalle de columnas y el ERD completo se desarrolla en la Parte II, sección 12.4):

| **Tabla** | **Descripción** |
| --- | --- |
| contracts | Almacena los contratos individuales con sus atributos (entidad, contratista, valor, fecha, estado). |
| entities | Almacena las entidades gubernamentales normalizadas, evitando duplicidad por variantes de nombre. |
| suppliers | Almacena los contratistas/proveedores asociados a los contratos. |

# 7. Criterios de Aceptación

- El pipeline extrae correctamente registros de al menos una fuente pública configurada (SECOP o Datos Abiertos Colombia).

- Los nombres de entidades con variantes conocidas se consolidan bajo una única forma canónica en la base de datos.

- Ningún registro con valor ≤ 0 o fecha nula se persiste en la base de datos.

- Las tablas contracts, entities y suppliers se pueblan de forma consistente y relacionada.

- El dashboard permite visualizar y filtrar los contratos cargados.

- El pipeline puede ejecutarse de extremo a extremo mediante un flujo de GitHub Actions.

- El sistema puede levantarse mediante Docker sin configuración manual adicional más allá de variables de entorno.

# 8. Trazabilidad (qué demuestra el proyecto)

Este SRS sustenta un proyecto cuyo valor demostrativo, de cara a un reclutador técnico, cubre las siguientes competencias:

- Web scraping con Python (Requests, BeautifulSoup).

- Procesos ETL completos (Extract, Transform, Load).

- Calidad y validación de datos.

- Modelado y gestión de bases de datos relacionales (PostgreSQL, SQLAlchemy).

- Arquitectura de software por componentes (pipeline desacoplado).

- Manejo de datos gubernamentales abiertos.

# Parte II — Documento de Arquitectura de Software

# 9. Introducción a la Arquitectura

## 9.1 Propósito

Esta parte identifica las necesidades arquitectónicas (atributos de calidad y drivers de diseño) del Sistema de Recolección de Datos de Contratación Pública, y presenta la arquitectura de software propuesta para satisfacerlas. Corresponde a la fase de Diseño del SDLC, tomando como entrada la Parte I (SRS) de este mismo documento.

## 9.2 Alcance

Se documenta la arquitectura a nivel de componentes principales del pipeline ETL (extracción, transformación, validación, carga), su despliegue mediante contenedores, su orquestación mediante CI/CD, y la capa de visualización. No se detalla el diseño de bajo nivel de cada módulo (clases, funciones), el cual corresponde a un documento de diseño detallado posterior.

# 10. Necesidades de Arquitectura

## 10.1 Atributos de calidad (Quality Attributes)

A partir de los requerimientos funcionales y no funcionales de la Parte I, se identifican los siguientes atributos de calidad como impulsores principales del diseño arquitectónico:

| **Atributo de calidad** | **Necesidad concreta** | **Prioridad** |
| --- | --- | --- |
| Modificabilidad | Cada fuente nueva (ej. un nuevo portal de contratación) debe poder agregarse sin modificar las etapas de transformación, validación o carga. | Alta |
| Calidad de datos / Integridad | Ningún registro inconsistente (valor ≤ 0, fecha nula, entidad no resoluble) debe llegar a las tablas finales. | Alta |
| Trazabilidad | Todo registro cargado debe poder rastrearse hasta su fuente y fecha de extracción. | Alta |
| Portabilidad | El sistema debe ejecutarse igual en la máquina de un desarrollador, en CI y en un servidor de despliegue. | Alta |
| Automatización / Operabilidad | El pipeline completo debe poder ejecutarse sin intervención manual, de forma programada. | Media |
| Escalabilidad de datos | El modelo debe soportar el crecimiento del volumen de contratos sin rediseño del esquema. | Media |
| Observabilidad | Cada ejecución del pipeline debe dejar evidencia (logs, métricas de registros aceptados/rechazados) para diagnóstico. | Media |
| Seguridad de credenciales | Las credenciales de base de datos no deben residir en el código fuente ni en el repositorio. | Alta |
| Usabilidad del dashboard | Un usuario no técnico debe poder explorar los contratos sin entrenamiento previo. | Media |

## 10.2 Drivers arquitectónicos y decisiones asociadas

Cada necesidad identificada se traduce en una decisión de diseño concreta:

| **Driver / necesidad** | **Decisión arquitectónica** |
| --- | --- |
| Múltiples fuentes con formatos distintos | Arquitectura en capas con un adaptador de extracción por fuente, detrás de una interfaz común. |
| Inconsistencia de nombres de entidades (MinTIC / MIN TIC / Ministerio TIC) | Capa de normalización independiente, basada en un diccionario/tabla de mapeo extensible. |
| Necesidad de garantizar calidad antes de persistir | Etapa explícita de validación entre transformación y carga, con reglas declarativas (assert) y un canal de rechazo (log de errores). |
| Reproducibilidad y despliegue consistente | Empaquetado de cada componente en contenedores Docker, orquestados con docker-compose. |
| Ejecución periódica sin intervención humana | Orquestación del pipeline mediante GitHub Actions (cron / disparo manual). |
| Consulta y exploración por usuarios no técnicos | Capa de presentación (dashboard) desacoplada de la base de datos transaccional, consumiendo solo vistas de lectura. |

## 10.3 Restricciones técnicas

- El stack tecnológico está definido de antemano: Python, Requests, BeautifulSoup, Pandas, PostgreSQL, SQLAlchemy, Docker y GitHub Actions.

- Las fuentes de datos son externas y no controladas por el equipo del proyecto; su estructura puede cambiar sin previo aviso.

- El sistema debe poder ejecutarse en infraestructura limitada (entorno de portafolio/demostración), por lo que la arquitectura debe ser ligera y no depender de servicios administrados costosos.

# 11. Estilo Arquitectónico Seleccionado

Se adopta un estilo de arquitectura en pipeline (tuberías y filtros), combinado con una separación en capas lógicas (extracción, transformación/validación, persistencia, presentación). Este estilo se ajusta naturalmente a un proceso ETL: cada etapa consume la salida de la anterior, puede probarse de forma aislada, y nuevas fuentes o reglas pueden incorporarse sin alterar las demás etapas.

**Justificación de la elección:**

- Modificabilidad: agregar una nueva fuente implica crear un nuevo adaptador de extracción, sin tocar transformación, validación o carga.

- Calidad de datos: la validación queda aislada como una etapa explícita y auditable entre la transformación y la carga.

- Operabilidad: cada etapa puede ejecutarse, probarse y desplegarse de forma independiente dentro de contenedores Docker.

- Trazabilidad: el flujo unidireccional de datos facilita registrar el origen y estado de cada registro en cada etapa.

# 12. Arquitectura de Componentes

## 12.1 Vista general del pipeline

Fuentes Publicas -> Extractor -> Normalizador -> Validador -> Cargador -> PostgreSQL -> Dashboard

*La orquestación (GitHub Actions) dispara la ejecución del pipeline completo; el entorno de contenedores (Docker) garantiza que cada etapa se ejecute de forma reproducible.*

## 12.2 Componentes y responsabilidades

| **Componente** | **Responsabilidad** | **Tecnología** |
| --- | --- | --- |
| Extractor (src/extract/) | Obtiene HTML/JSON de cada fuente pública y lo convierte en registros crudos (entidad, contratista, valor, fecha, estado). | Python, Requests, BeautifulSoup |
| Normalizador (src/transform/) | Resuelve variantes de nombres de entidades a su forma canónica y estandariza tipos de datos (fechas, montos). | Python, Pandas |
| Validador (src/transform/) | Aplica reglas de calidad (valor > 0, fecha no nula, entidad resuelta) y separa registros válidos de rechazados. | Python, Pandas |
| Cargador (src/load/) | Inserta los registros válidos en PostgreSQL respetando las relaciones entre contracts, entities y suppliers, evitando duplicados. | SQLAlchemy |
| Base de datos | Almacena el modelo relacional consolidado y sirve como fuente única de verdad para el análisis. | PostgreSQL |
| Dashboard | Expone visualizaciones y filtros sobre los datos consolidados para el usuario final. | Python (framework de visualización) + SQL de solo lectura |
| Orquestador CI/CD | Programa y ejecuta el pipeline de extremo a extremo, y corre pruebas automatizadas. | GitHub Actions |
| Entorno de ejecución | Empaqueta cada componente para garantizar que el comportamiento sea idéntico en cualquier entorno. | Docker, Docker Compose |

## 12.3 Manejo de Rechazos (detalle)

La validación no es una simple compuerta binaria: es un punto de decisión que clasifica cada registro y lo enruta a uno de dos destinos, sin detener el flujo del pipeline.

### 12.3.1 Reglas de rechazo

| **Regla** | **Condición de rechazo** | **Campo afectado** |
| --- | --- | --- |
| Valor positivo | valor <= 0 o valor es nulo | contracts.valor |
| Fecha válida | fecha es nula o no parseable | contracts.fecha |
| Entidad resoluble | el nombre de entidad no puede normalizarse a una forma canónica conocida | entities.nombre |
| Duplicado exacto | ya existe un registro con la misma fuente, entidad, contratista, valor y fecha | contracts (clave compuesta) |

### 12.3.2 Ciclo de vida de un registro rechazado

Registro crudo -> Validador -> ¿cumple todas las reglas?
   SI  -> continua hacia el Cargador -> PostgreSQL
   NO  -> se enriquece con motivo de rechazo -> rejected_records (tabla) + log de ejecucion

Cada registro rechazado no se descarta silenciosamente: se persiste en una tabla de rechazos (rejected_records) con el motivo específico, la fuente de origen y la marca de tiempo. Esto permite, más adelante, reprocesar registros si se corrige la fuente o se ajusta una regla, sin perder evidencia de lo ocurrido.

| **Columna** | **Tipo** | **Descripción** |
| --- | --- | --- |
| id | SERIAL PK | Identificador del registro rechazado. |
| fuente | VARCHAR | Fuente de origen (ej. SECOP, Datos Abiertos). |
| payload_crudo | JSONB | Registro original tal como llegó del extractor, sin transformar. |
| motivo_rechazo | VARCHAR | Regla que falló (ej. 'valor_no_positivo', 'fecha_nula'). |
| fecha_rechazo | TIMESTAMP | Momento en que se ejecutó la validación. |

### 12.3.3 Por qué se diseña así

- Disponibilidad del pipeline: un registro defectuoso nunca debe detener la carga de los demás registros válidos del mismo lote.

- Trazabilidad: guardar el payload crudo permite diagnosticar si el problema está en la fuente, en el scraping o en una regla de validación demasiado estricta.

- Reprocesamiento: si se corrige el diccionario de normalización de entidades, los registros rechazados por 'entidad no resoluble' pueden re-ejecutarse contra el validador sin volver a scrapear la fuente.

## 12.4 Modelo de Datos Detallado (ERD)

La base de datos PostgreSQL organiza la información en tres tablas relacionadas, más la tabla de rechazos descrita arriba. A continuación el detalle de columnas de cada tabla.

### 12.4.1 Tabla entities

| **Columna** | **Tipo** | **Descripción** |
| --- | --- | --- |
| id | SERIAL PK | Identificador único de la entidad. |
| nombre_canonico | VARCHAR UNIQUE | Forma normalizada del nombre (ej. 'Ministerio de Tecnologías...'). |
| sigla | VARCHAR | Sigla principal de la entidad, si aplica. |
| creado_en | TIMESTAMP | Fecha de primera aparición de la entidad en el sistema. |

### 12.4.2 Tabla suppliers

| **Columna** | **Tipo** | **Descripción** |
| --- | --- | --- |
| id | SERIAL PK | Identificador único del contratista. |
| nombre | VARCHAR | Nombre del contratista/proveedor. |
| nit_o_id_fiscal | VARCHAR | Identificador fiscal, si la fuente lo provee. |
| creado_en | TIMESTAMP | Fecha de primera aparición del contratista en el sistema. |

### 12.4.3 Tabla contracts

| **Columna** | **Tipo** | **Descripción** |
| --- | --- | --- |
| id | SERIAL PK | Identificador único del contrato. |
| entity_id | INTEGER FK -> entities.id | Entidad contratante. |
| supplier_id | INTEGER FK -> suppliers.id | Contratista adjudicado. |
| valor | NUMERIC(18,2) | Valor del contrato; debe ser mayor a 0. |
| fecha | DATE | Fecha del contrato; no puede ser nula. |
| estado | VARCHAR | Estado del contrato (ej. en ejecución, terminado, liquidado). |
| fuente | VARCHAR | Fuente de origen del registro, para trazabilidad. |
| extraido_en | TIMESTAMP | Marca de tiempo de extracción del dato. |

### 12.4.4 Relaciones

- entities (1) -> (N) contracts: una entidad puede tener muchos contratos.

- suppliers (1) -> (N) contracts: un contratista puede tener muchos contratos.

- Restricción de unicidad en entities.nombre_canonico para impedir duplicados por variantes de nombre.

# 13. Vista de Despliegue

El sistema se empaqueta en contenedores Docker independientes, coordinados mediante Docker Compose. La tabla siguiente resume los contenedores, sus puertos/volúmenes y cómo se conectan entre sí.

| **Contenedor** | **Imagen base** | **Contenido** | **Expone / Persiste** |
| --- | --- | --- | --- |
| etl | python:3.12-slim | Código del pipeline (extract, transform, load), Requests, BeautifulSoup, Pandas, SQLAlchemy. | Variables de entorno con credenciales de DB; sin puertos expuestos. |
| db | postgres:16 | Esquemas contracts, entities, suppliers, rejected_records. | Puerto 5432 (solo red interna); volumen persistente para los datos. |
| dashboard | python:3.12-slim | Aplicación de visualización con acceso de solo lectura a la base de datos. | Puerto 8080 expuesto al usuario. |

## 13.1 Red y dependencias entre contenedores

- Los tres contenedores se conectan a una misma red interna de Docker Compose; solo el contenedor dashboard expone un puerto hacia afuera.

- El contenedor etl depende de que db esté disponible (healthcheck) antes de ejecutar la carga.

- El contenedor dashboard se conecta a db con un usuario de solo lectura, distinto del usuario que usa etl para escribir.

## 13.2 Orquestación externa (CI/CD)

GitHub Actions actúa como orquestador externo: construye las imágenes, ejecuta pruebas automatizadas y dispara la ejecución periódica o manual del pipeline ETL (docker compose run etl), gestionando las credenciales de base de datos mediante secretos del repositorio en lugar de archivos de configuración versionados.

# 14. Tácticas de Diseño por Atributo de Calidad

| **Atributo de calidad** | **Táctica aplicada en la arquitectura** |
| --- | --- |
| Modificabilidad | Interfaz común de extracción; cada fuente se implementa como un adaptador independiente. |
| Calidad de datos | Etapa de validación explícita con reglas declarativas y canal de rechazo separado. |
| Trazabilidad | Cada registro conserva un identificador de fuente y marca de tiempo de extracción. |
| Portabilidad | Empaquetado completo en contenedores Docker con configuración por variables de entorno. |
| Operabilidad | Automatización del pipeline end-to-end mediante GitHub Actions. |
| Seguridad | Gestión de credenciales mediante secretos de CI/CD, nunca en el código fuente. |
| Observabilidad | Registro de logs por etapa, incluyendo conteo de registros aceptados y rechazados. |

# 15. Riesgos Arquitectónicos y Mitigaciones

| **Riesgo** | **Mitigación** |
| --- | --- |
| Cambios en la estructura HTML de las fuentes públicas rompen el scraping. | Aislar la lógica de parsing en adaptadores independientes por fuente, con pruebas que detecten cambios estructurales. |
| Crecimiento del volumen de datos degrada el rendimiento de consultas. | Definir índices sobre las claves de consulta frecuente (entidad, fecha) desde el diseño del esquema. |
| Normalización incompleta de entidades genera duplicados. | Mantener el diccionario de normalización como dato versionado y revisable, no embebido en el código. |
| Fallos en la ejecución automatizada pasan inadvertidos. | Notificaciones o reportes de fallo en el flujo de GitHub Actions, y logs persistentes por ejecución. |

# 16. Plan de Desarrollo por Fases (Desarrollador Único)

Al no existir un equipo, las fases se secuencian en lugar de paralelizarse, priorizando siempre tener un pipeline ejecutable de extremo a extremo lo antes posible (aunque sea con una sola fuente), y luego ampliar cobertura y robustez.

## Fase 0 - Preparación del entorno

| **Tarea** | **Entregable** |
| --- | --- |
| Inicializar repositorio Git y estructura de carpetas (src/extract, src/transform, src/load, tests). | Repositorio base. |
| Definir docker-compose.yml con los servicios db y etl (sin dashboard todavía). | Entorno local levantando PostgreSQL. |
| Crear el esquema inicial de base de datos (entities, suppliers, contracts, rejected_records). | Migraciones / script SQL inicial. |

## Fase 1 - Extracción de una sola fuente

*Fuente elegida: el dataset “SECOP II - Contratos Electrónicos” publicado en datos.gov.co (portal Socrata), consumido vía la API SODA (Socrata Open Data API) en lugar de scraping HTML. Esta API expone el mismo dato que SECOP, con filtros, paginación y respuesta en JSON, lo que la hace más estable que parsear páginas web.*

| **Tarea** | **Entregable** |
| --- | --- |
| Identificar el endpoint SODA del dataset (https://www.datos.gov.co/resource/{dataset_id}.json) y los parámetros de consulta soportados ($select, $where, $limit, $offset). | Documento corto de referencia del endpoint y campos relevantes (entidad, contratista, valor, fecha, estado). |
| Implementar el adaptador de extracción usando Requests contra la API SODA, con paginación por $limit/$offset para recorrer el dataset completo. | Módulo src/extract/secop_socrata.py con datos crudos en memoria o archivo intermedio. |
| Manejar límites de la API (rate limiting, tamaño máximo de respuesta) y, si se requiere mayor cuota, registrar un App Token de Socrata. | Cliente HTTP resiliente con reintentos y App Token configurado vía variable de entorno. |
| Escribir pruebas unitarias del adaptador con una respuesta JSON de muestra guardada como fixture, para no depender de la red en cada prueba. | tests/test_extract.py. |

## Fase 2 - Transformación y validación

| **Tarea** | **Entregable** |
| --- | --- |
| Implementar el diccionario de normalización de entidades y la función de resolución a nombre canónico. | src/transform/normalize.py. |
| Implementar las reglas de validación (valor > 0, fecha no nula, entidad resoluble) y el enrutamiento a rejected_records. | src/transform/validate.py. |
| Pruebas unitarias con casos límite: valor 0, valor negativo, fecha nula, variantes de 'MinTIC'. | tests/test_transform.py. |

## Fase 3 - Carga a PostgreSQL

| **Tarea** | **Entregable** |
| --- | --- |
| Implementar los modelos SQLAlchemy para entities, suppliers, contracts, rejected_records. | src/load/models.py. |
| Implementar la función de carga idempotente (evitar duplicados al re-ejecutar el pipeline). | src/load/loader.py. |
| Prueba de extremo a extremo: ejecutar extract -> transform -> validate -> load contra la base de datos del contenedor db. | tests/test_pipeline_e2e.py. |

## Fase 4 - Segunda fuente y generalización

*Segunda fuente: scraping HTML directo del sitio de SECOP, para cubrir procesos o campos que no estén disponibles en el dataset de datos.gov.co. Esta fuente es más frágil que la API SODA de la Fase 1, por lo que se aborda después de tener el pipeline ya probado de extremo a extremo.*

| **Tarea** | **Entregable** |
| --- | --- |
| Definir la interfaz común de extracción (clase base o protocolo) a partir de lo aprendido con el adaptador de la API SODA. | src/extract/base.py. |
| Implementar el adaptador de scraping para SECOP (Requests + BeautifulSoup), reutilizando normalización, validación y carga sin cambios. | src/extract/secop_scraper.py. |

## Fase 5 - Automatización (CI/CD)

| **Tarea** | **Entregable** |
| --- | --- |
| Configurar un workflow de GitHub Actions que corra las pruebas en cada push. | .github/workflows/test.yml. |
| Configurar un workflow programado (cron) que ejecute el pipeline completo y use secretos para las credenciales de base de datos. | .github/workflows/run_pipeline.yml. |

## Fase 6 - Dashboard

| **Tarea** | **Entregable** |
| --- | --- |
| Implementar consultas de solo lectura para los filtros principales (entidad, contratista, rango de fechas, estado). | src/dashboard/queries.py. |
| Construir la interfaz de visualización y agregarla como servicio adicional en docker-compose.yml. | Servicio dashboard funcionando end-to-end. |

## Fase 7 - Cierre y documentación

| **Tarea** | **Entregable** |
| --- | --- |
| Completar README con instrucciones de ejecución local y arquitectura resumida. | README.md. |
| Revisar logs y métricas de aceptación/rechazo con datos reales, ajustar reglas si hay falsos rechazos. | Reporte de calidad de datos. |

*Nota de secuenciación: cada fase deja el sistema en un estado funcional y demostrable; no es necesario completar todas las fuentes ni el dashboard para tener algo que mostrar. Esto es importante para un desarrollador único, ya que permite detenerse en cualquier fase con un artefacto coherente.*
