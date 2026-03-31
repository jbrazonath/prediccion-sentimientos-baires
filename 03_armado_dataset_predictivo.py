import pandas as pd
import re

print("Iniciando Paso 3: Construcción del Dataset Predictivo...\n")

# 1. Cargar el dataset que ya tiene los sentimientos de PySentimiento
df = pd.read_csv('dataset_con_sentimiento.csv')

# 2. Filtrar únicamente las REACCIONES (estas son las que tienen el texto del "anuncio" guardado en 'referencia_anuncio')
# Las "MENCIONES_DIRECTAS" son tuits orgánicos de la gente quejándose o felicitando sin responderle a un anuncio específico.
df_reacciones = df[df['tipo'] == 'REACCION'].copy()
print(f"Total de respuestas (reacciones) a analizar: {len(df_reacciones)}")

# Si hay filas donde no existe referencia_anuncio, las descartamos
df_reacciones = df_reacciones.dropna(subset=['referencia_anuncio'])

# 3. Agrupamiento por Anuncio
# Agrupamos por el Anuncio, el Pilar y contamos cuántas reacciones Positivas, Negativas y Neutras tuvo cada uno.
# Usamos unstack para que POS, NEG, NEU se conviertan en columnas independientes.
df_agrupado = df_reacciones.groupby(
    ['referencia_anuncio', 'pilar']
)['sentimiento'].value_counts().unstack(fill_value=0).reset_index()

# Si por alguna razón un anuncio no tuvo de algún tipo, aseguramos que la columna exista
for col in ['NEG', 'NEU', 'POS']:
    if col not in df_agrupado.columns:
        df_agrupado[col] = 0

# 4. Cálculo de Porcentajes y Etiqueta Dominante (Variable Y final)
df_agrupado['total_respuestas'] = df_agrupado['NEG'] + df_agrupado['NEU'] + df_agrupado['POS']

# Evitamos divisiones por 0
df_agrupado = df_agrupado[df_agrupado['total_respuestas'] > 0]

df_agrupado['%_NEG'] = (df_agrupado['NEG'] / df_agrupado['total_respuestas']) * 100
df_agrupado['%_NEU'] = (df_agrupado['NEU'] / df_agrupado['total_respuestas']) * 100
df_agrupado['%_POS'] = (df_agrupado['POS'] / df_agrupado['total_respuestas']) * 100

# La emoción predominante (El sentimiento que ganó la votación popular)
df_agrupado['sentimiento_predominante'] = df_agrupado[['NEG', 'NEU', 'POS']].idxmax(axis=1)

# 5. Limpieza Final del Anuncio (Para que sirva de variable X modelo)
def limpiar_anuncio(texto):
    texto = str(texto)
    texto = re.sub(r'http\S+', '', texto) # Quitar links
    texto = re.sub(r'@\w+', '', texto) # Quitar menciones
    texto = re.sub(r'[\r\n]+', ' ', texto) 
    return re.sub(r'\s+', ' ', texto).strip()

df_agrupado['texto_anuncio_limpio'] = df_agrupado['referencia_anuncio'].apply(limpiar_anuncio)

# Reordenamos columnas para que quede prolijo: X1, X2 -> Y1, Y2...
columnas_finales = [
    'texto_anuncio_limpio', 'pilar', 'total_respuestas', 
    'NEG', 'NEU', 'POS', 
    '%_NEG', '%_NEU', '%_POS', 
    'sentimiento_predominante'
]
df_final = df_agrupado[columnas_finales].copy()

# Guardar Dataset Final
archivo_predictivo = 'dataset_entrenamiento_predictivo.csv'
df_final.to_csv(archivo_predictivo, index=False)

print(f"\n✅ Dataset Predictivo creado exitosamente con {len(df_final)} anuncios únicos.")
print(f"Archivo guardado como: '{archivo_predictivo}'")

print("\n--- Vista Previa de los 3 Anuncios con Más Respuestas ---")
top = df_final.sort_values('total_respuestas', ascending=False).head(3)
for idx, row in top.iterrows():
    print(f"\n📢 ANUNCIO ({row['pilar']}): {row['texto_anuncio_limpio'][:100]}...")
    print(f"📊 Reacción Dominante: {row['sentimiento_predominante']} (Basado en {row['total_respuestas']} rtas)")
    print(f"   -> 😡 NEG: {row['%_NEG']:.1f}% | 😐 NEU: {row['%_NEU']:.1f}% | 😃 POS: {row['%_POS']:.1f}%")
