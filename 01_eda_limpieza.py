import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

# Configuración visual para los gráficos
sns.set_theme(style="whitegrid")

print("Iniciando proceso de EDA y Limpieza...")

# 1. UNIFICACIÓN DE LOS DATASETS
archivos = {
    'Cultura': 'dataset_recolectado_CULTURA.csv',
    'Ambiente': 'dataset_recolectado_AMBIENTE.csv',
    'Transporte': 'dataset_recolectado_TRANSPORTE.csv'
}

dfs = []
for pilar, archivo in archivos.items():
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        df['pilar'] = pilar  # Nueva columna para identificar la categoría
        dfs.append(df)
    else:
        print(f"Advertencia: No se encontró el archivo {archivo}")

df_unificado = pd.concat(dfs, ignore_index=True)

# 2. ELIMINACIÓN DE COLUMNAS INNECESARIAS PARA NLP (IDs)
# id_tuit y id_conversacion eran vitales para la recolección, pero el modelo de texto no los necesita.
columnas_a_eliminar = ['id_tuit', 'id_conversacion']
df_unificado = df_unificado.drop(columns=columnas_a_eliminar, errors='ignore')

# 3. LIMPIEZA DE NULOS Y DUPLICADOS EN TEXTO
print("\n--- Estado Inicial ---")
print(f"Total de registros originales: {len(df_unificado)}")
print("Nulos por columna:\n", df_unificado.isnull().sum())

# En NLP, si no hay texto, la fila no sirve para nada.
df_unificado = df_unificado.dropna(subset=['texto'])

# Eliminamos tuits con el mismo texto exacto (por si hay spam transversal o bots)
# Primero ordenamos por 'rts' descendente para quedarnos con el tuit original que tenga más interacciones reales
if 'rts' in df_unificado.columns:
    df_unificado['rts'] = pd.to_numeric(df_unificado['rts'], errors='coerce').fillna(0).astype(int)
    df_unificado = df_unificado.sort_values('rts', ascending=False)

df_unificado = df_unificado.drop_duplicates(subset=['texto'])

print("\n--- Después de quitar duplicados de texto y nulos ---")
print(f"Total de registros originales únicos útiles: {len(df_unificado)}")

# 3.5 EXPANSIÓN POR RETUITS (RTS)
# Tal como solicitaste, consideramos cada retuit como una interacción / línea nueva.
if 'rts' in df_unificado.columns:
    # El +1 cuenta al tuit original. Ej: si tiene 5 RTs, entonces habrá 6 filas idénticas de ese texto.
    df_unificado = df_unificado.loc[df_unificado.index.repeat(df_unificado['rts'] + 1)].reset_index(drop=True)
    print("\n--- Después de expandir por Retuits (Nuevas Filas) ---")
    print(f"Total de interacciones para entrenar el modelo NLP: {len(df_unificado)}")

# 4. LIMPIEZA DE TEXTO A CONSIDERACIÓN DEL MODELO (PREPROCESAMIENTO)
def limpiar_texto(texto):
    texto = str(texto) # Mantenemos mayúsculas originales (importante para detectar intensidad/emoción)
    texto = re.sub(r'http\S+', '', texto) # Eliminar links (URLs) que no aportan sentimiento
    texto = re.sub(r'@\w+', '', texto) # Eliminar menciones (@usuario) para no sesgar
    texto = re.sub(r'[\r\n]+', ' ', texto) # Quitar los saltos de línea molestos
    texto = re.sub(r'\s+', ' ', texto).strip() # Quitar espacios extra repetidos
    # Fíjate que en ningún momento tocamos signos de puntuación o EMOJIS.
    return texto

print("\nLimpiando el texto (eliminando links, menciones, etc. pero manteniendo Emojis y Mayúsculas)...")
df_unificado['texto_limpio'] = df_unificado['texto'].apply(limpiar_texto)

# Si un tuit solo era un link o una mención, al limpiarlo quedará vacío. Lo borramos.
df_unificado = df_unificado[df_unificado['texto_limpio'] != '']

# 5. GUARDAR SIN DESTRUIR EL TRABAJO ANTERIOR
# Guardamos en un archivo nuevo para preservar los recolectados originales.
df_unificado.to_csv('dataset_unificado_limpio.csv', index=False)
print("✅ Archivo guardado con éxito: 'dataset_unificado_limpio.csv'")

# 6. ANÁLISIS EXPLORATORIO (EDA) - ESTADÍSTICAS Y GRÁFICOS
print("\n--- Distribución Final ---")
print("\nPor Pilar de Gestión:")
print(df_unificado['pilar'].value_counts())

print("\nPor Tipo de Tuit:")
print(df_unificado['tipo'].value_counts())

# Crear gráfico 1: Distribución general
plt.figure(figsize=(8, 5))
sns.countplot(data=df_unificado, x='pilar', hue='tipo', palette='viridis')
plt.title('Distribución de Tuits Recolectados por Pilar y Tipo', fontsize=14)
plt.ylabel('Cantidad de Tuits', fontsize=12)
plt.xlabel('Pilar', fontsize=12)
plt.tight_layout()
plt.savefig('eda_distribucion_tipos.png')
print("\n✅ Gráfico 1 guardado como: 'eda_distribucion_tipos.png'")

# Gráfico 2: Top de fechas más activas (Días con más tuits)
# Convertimos la fecha (que está como string ISO) a datetime sacando la hora
df_unificado['fecha_corta'] = pd.to_datetime(df_unificado['fecha']).dt.date
top_dias = df_unificado['fecha_corta'].value_counts().nlargest(10)

plt.figure(figsize=(10, 5))
sns.barplot(x=top_dias.index, y=top_dias.values, color='coral')
plt.title('Top 10 Días con Mayor Volumen de Tuits', fontsize=14)
plt.xticks(rotation=45)
plt.ylabel('Cantidad')
plt.xlabel('Fecha')
plt.tight_layout()
plt.savefig('eda_volumen_diario.png')
print("✅ Gráfico 2 guardado como: 'eda_volumen_diario.png'")
