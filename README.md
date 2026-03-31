## Predicción de Sentimiento Ciudadano ante Políticas Públicas

Este repositorio contiene la arquitectura de procesamiento de lenguaje natural (NLP) diseñada para analizar y predecir la reacción ciudadana frente a anuncios del Gobierno de la Ciudad Autónoma de Buenos Aires (GCBA).

El objetivo principal de la investigación es desarrollar un modelo predictivo capaz de inferir la distribución del sentimiento (positivo, negativo o neutro) de la población basándose en el texto de un anuncio gubernamental y la temática del mismo.

El proceso de datos (pipeline) está modularizado en tres etapas iniciales de procesamiento de la información.

## 01_eda_limpieza.py: Unificación y Data Augmentation

Este script representa el primer paso del proceso ETL (Extract, Transform, Load). Toma los datos crudos recolectados de Twitter correspondientes a los tres grandes pilares de la gestión (Transporte, Cultura y Ambiente) y realiza las siguientes operaciones:

1. **Unificación y Etiquetado:** Une los archivos CSV de cada pilar en un único conjunto de datos, creando la variable "pilar" para rastrear el origen temático de cada interacción.
2. **Eliminación de Outliers:** Descarta los registros con valores nulos o vacíos en el campo de texto, ya que carecen de utilidad para un modelo de NLP.
3. **Limpieza de Texto Base:** Aplica expresiones regulares para eliminar enlaces web (URLs) y menciones directas a cuentas de usuario de la red social. Para no obstaculizar la detección posterior de intensidad por parte de los transformers, no se alteran las mayúsculas originales ni se borran los emoticones.
4. **Data Augmentation:** Se efectúa un paso crítico para asignar peso orgánico a las interacciones masivas. Utilizando la cantidad de retuits como una métrica de adhesión al sentimiento de un usuario particular, el código multiplica la fila original según su índice de retuits. Esto garantiza que una postura fuertemente apoyada por la ciudadanía tenga una ponderación estadística en el modelo, transformando cerca de 6.000 tuits únicos en más de 18.000 interacciones ponderadas, sin falsear o inventar información artificial.
5. **Análisis Exploratorio de Datos (EDA):** Genera estadísticas iniciales y gráficos de distribución por pilar y volumen diario, exportados en formato PNG.

El resultado se exporta a: `dataset_unificado_limpio.csv`.

## 02_analisis_sentimiento.py: Etiquetado de Variable Foco

Dado que la información recolectada no contaba con etiquetas para emplear aprendizaje supervisado, este script se encarga de crear la variable objetivo (Variable Y) utilizando técnicas de aprendizaje de lenguaje mediante modelos preentrenados (Transfer Learning).

1. **Carga y Depuración de Extremos:** Importa el conjunto limpio y elimina aquellos mensajes extremadamente cortos (inferiores a 5 caracteres) que carecen de cohesión semántica como para inferir emocion alguna (por ejemplo un caracter suelto o una sílaba).
2. **Uso de PySentimiento:** Instancia localmente una versión entrenada sobre la arquitectura de RoBERTa, ajustada al español. Dicha arquitectura basada en atención y transformers ha demostrado ser un estado del arte para tareas semánticas.
3. **Optimización por Lotes (Batch Size):** Para evitar la saturación de los recursos computacionales al procesar más de 18.000 secuencias de texto complejas, la inferencia de PySentimiento se ejecuta en bloques (batches) sucesivos.
4. **Generación de Variable Foco:** El modelo asigna a cada interacción una etiqueta de tres vías: POS (Positivo), NEG (Negativo) o NEU (Neutro).

El resultado se exporta a: `dataset_con_sentimiento.csv`.

## 03_armado_dataset_predictivo.py: Arquitectura Entrada-Salida

Para concretar la meta académica, el conjunto de datos de sentimientos individuales debe ser agrupado a nivel de la publicación gubernamental propiamente dicha. Este script diseña la estructura tabular que servirá para la alimentación del algoritmo final de Machine Learning.

1. **Aislamiento Orgánico:** Filtra y se queda exclusivamente con aquellas tuits clasificados como "REACCION", dejando de lado menciones directas huérfanas o tuits orgánicos de usuarios donde no existiese un anuncio como factor desencadenante. Todo dentro del dataset final debe responder a una acción o comunicación oficial.
2. **Agrupación y Distribución Matemática:** Toma el texto del anuncio oficial como constante y evalúa el total de las respuestas que dicho discurso produjo. Se transponen y computan matemáticamente los cálculos para determinar, sobre el 100% de las réplicas, cómo se dividieron las proporciones entre las tres emociones.
3. **Variable X e Y:** Prepara el conjunto final mediante dos variables predictoras asociadas a un resultado (label).
   - Variable X1: El Pilar o Categoría del Anuncio.
   - Variable X2: El bloque de texto del Anuncio.
   - Variable Y: El Sentimiento Predominante del público (El sentimiento con el máximo porcentaje estadístico) así como los índices desglosados para posibilitar posteriores tareas de regresión.

El resultado se exporta a: `dataset_entrenamiento_predictivo.csv`, proveyendo un dataset supervisado condensado y perfecto para tareas de clasificación predictiva futura.
