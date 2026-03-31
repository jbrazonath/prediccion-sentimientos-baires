import pandas as pd
from pysentimiento import create_analyzer
from tqdm import tqdm

print("Iniciando Paso 2: Análisis de Sentimiento...")

# 1. Cargar el dataset limpio
archivo_entrada = 'dataset_unificado_limpio.csv'
df = pd.read_csv(archivo_entrada)
print(f"Dataset cargado con {len(df)} registros.")

# 2. LIMPIEZA DE OUTLIERS
# Eliminamos textos demasiado cortos que no aportan sentimiento (ej: "ok", "a", "jaja")
# Establecemos un umbral mínimo de 5 caracteres.
registros_antes = len(df)
df['texto_limpio'] = df['texto_limpio'].astype(str)
df['len_texto'] = df['texto_limpio'].apply(len)

# Nos quedamos con los que tienen 5 caracteres o más
df = df[df['len_texto'] >= 5].copy()
registros_despues = len(df)
print(f"Outliers eliminados (textos muy cortos): {registros_antes - registros_despues}")
print(f"Dataset útil final para clasificar: {registros_despues} registros.\n")

# Borramos la columna 'len_texto' porque ya no nos sirve
df = df.drop(columns=['len_texto'])

# 3. CARGAR EL MODELO
print("Descargando/Cargando el modelo transformer 'pysentimiento' (RoBERTa)...")
# Esto tomará un momentito la primera vez pues descargará los pesos del modelo.
analyzer = create_analyzer(task="sentiment", lang="es")

# 4. PREDICCIÓN CON BATCH SIZE Y BARRA DE PROGRESO
textos = df['texto_limpio'].tolist()
resultados = []

# Definimos el tamaño del bloque (batch) para no colapsar la RAM
batch_size = 32

print(f"\nClasificando sentimientos en bloques de {batch_size}...")
for i in tqdm(range(0, len(textos), batch_size), desc="Analizando"):
    batch = textos[i:i + batch_size]
    
    # El modelo analiza la lista de tuits en paralelo
    preds = analyzer.predict(batch)
    
    # Cada predicción devuelve un objeto; extraemos la etiqueta (POS, NEG, NEU)
    for p in preds:
        resultados.append(p.output)

# Agregamos la nueva variable FOCO a nuestro dataset
df['sentimiento'] = resultados

# 5. GUARDAR RESULTADOS
archivo_salida = 'dataset_con_sentimiento.csv'
df.to_csv(archivo_salida, index=False)

print(f"\n✅ ¡Proceso finalizado! Se ha creado la Variable Foco.")
print("Distribución de sentimientos encontrados:")
print(df['sentimiento'].value_counts())
print(f"\nArchivo guardado como: '{archivo_salida}'")
