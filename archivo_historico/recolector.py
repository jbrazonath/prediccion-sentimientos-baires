
import tweepy
import csv
import time

# TUS CREDENCIALES
MY_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAALBc7gEAAAAA%2FW0dlWeiFe9YmICRgPSoDxB%2FAhs%3DsjGUmX0ha2nKP4AdMGKAHHmWouFRG9l4RVZrQYwNanaNekCCIJ"
client = tweepy.Client(bearer_token=MY_BEARER_TOKEN)

username = 'batransporte'

# --- 1. DEFINICIÓN DE LA QUERY ROBUSTA ---
# Explicación de los filtros:
# - (@{username}): Busca menciones directas.
# - (subte OR tarifa OR ...): FILTRO DE TEMA. Solo baja tweets que hablen de esto.
#   Esto es CLAVE para no gastar cuota en tweets irrelevantes (ej: "perdí mi paraguas").
# - -from:{username}: Excluye los tweets que publica la misma cuenta oficial.
# - lang:es: Solo español.
# - -is:retweet: Excluye RTs (querés opiniones originales).

keywords = "(subte OR tarifa OR aumento OR colectivo OR bondi OR tren OR servicio OR frecuencia OR paro OR boleto)"
query = f'(@{username}) {keywords} -from:{username} lang:es -is:retweet'

print(f"🔎 Query a ejecutar: {query}")
print("--- Buscando interacciones de calidad ---")

csv_filename = "dataset_transporte.csv"

try:
    # Pedimos campos adicionales necesarios para tu TP (métricas, autor, fecha exacta)
    response = client.search_recent_tweets(
        query=query,
        max_results=20, # Ajustá este número según tu presupuesto/prueba
        tweet_fields=['created_at', 'text', 'public_metrics', 'conversation_id', 'author_id'],
        expansions=['author_id'], # Para obtener datos del usuario si quisieras
        user_fields=['username']
    )

    if response.data:
        print(f"✅ Se encontraron {len(response.data)} tweets relevantes.\n")
        
        # Guardamos en CSV como pide el PDF (Requisito HU2/HU3)
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header según especificaciones del PDF (Página 9)
            writer.writerow(['fecha', 'usuario_id', 'texto', 'likes', 'retweets', 'conversation_id'])

            for tweet in response.data:
                metrics = tweet.public_metrics
                
                # Limpieza básica de texto (reemplazar saltos de línea para que no rompa el CSV)
                clean_text = tweet.text.replace('\n', ' ').replace('\r', '')

                writer.writerow([
                    tweet.created_at,
                    tweet.author_id,
                    clean_text,
                    metrics['like_count'],
                    metrics['retweet_count'],
                    tweet.conversation_id
                ])
                
                # Preview en consola
                print(f"💬 {clean_text[:60]}... | ❤️ {metrics['like_count']}")

        print(f"\n💾 Datos guardados exitosamente en: {csv_filename}")
        
    else:
        print("⚠️ No se encontraron tweets con esos filtros específicos.")

except Exception as e:
    print(f"❌ Error: {e}")