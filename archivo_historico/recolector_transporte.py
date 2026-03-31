import tweepy
import csv
import os
from config_twitter import BEARER_TOKEN

# --- CONFIGURACIÓN ---
username = 'basubte'
# Usamos la query optimizada para subte
keywords = "(subte OR tarifa OR aumento OR servicio OR frecuencia OR demora OR escalera OR estación OR combinación)"
query = f'(@{username}) {keywords} -from:{username} lang:es -is:retweet'

csv_filename = "dataset_transporte.csv"

def recolectar():
    print(f"🚀 Iniciando recolección para: {username}")
    print(f"🔎 Query: {query}")
    
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    try:
        # Buscamos los tweets (max_results 10 para la prueba inicial y no gastar cuota)
        response = client.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=['created_at', 'text', 'public_metrics', 'conversation_id', 'author_id']
        )

        if not response.data:
            print("⚠️ No se encontraron menciones recientes con esos filtros.")
            return

        print(f"✅ Se encontraron {len(response.data)} interacciones.")

        # Escribimos el CSV (si el archivo no existe, pone el header)
        file_exists = os.path.isfile(csv_filename)
        
        with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['fecha', 'usuario_id', 'texto', 'likes', 'retweets', 'conversation_id'])

            for tweet in response.data:
                m = tweet.public_metrics
                clean_text = tweet.text.replace('\n', ' ').replace('\r', '')
                writer.writerow([
                    tweet.created_at,
                    tweet.author_id,
                    clean_text,
                    m['like_count'],
                    m['retweet_count'],
                    tweet.conversation_id
                ])
        
        print(f"💾 Datos guardados en {csv_filename}")

    except Exception as e:
        print(f"❌ Error durante la recolección: {e}")

if __name__ == "__main__":
    recolectar()
