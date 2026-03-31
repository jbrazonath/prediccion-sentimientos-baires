import tweepy
import csv
import os
import time
from config_twitter import BEARER_TOKEN

# --- CONFIGURACIÓN ---
username = 'basubte'
# Keywords para filtrar respuestas con "sustancia"
keywords_respuestas = "(subte OR tarifa OR aumento OR servicio OR frecuencia OR demora OR escalera OR estación OR combinación OR sucio OR emova OR jorgemacri)"
csv_filename = "dataset_transporte_completo.csv"

def recolectar_conversaciones():
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    
    print(f"🔍 Buscando eventos y reacciones para @{username}...")

    # 1. Buscamos los últimos anuncios oficiales
    posts = client.search_recent_tweets(
        query=f"from:{username} -is:retweet",
        max_results=10, 
        tweet_fields=['created_at', 'text', 'conversation_id', 'public_metrics']
    )

    if not posts.data:
        print("⚠️ No hay anuncios recientes.")
        return

    # Preparar el CSV
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Agregamos 'texto_referencia' para guardar el tuit disparador en cada fila
            writer.writerow(['tipo', 'fecha', 'id_conversacion', 'texto_usuario', 'texto_referencia', 'likes', 'rts'])

        for post in posts.data:
            texto_anuncio = post.text.replace('\n', ' ')
            print(f"\n📢 Anuncio detectado: {texto_anuncio[:60]}...")
            
            # Guardamos el anuncio como fila de referencia
            writer.writerow(['ANUNCIO', post.created_at, post.conversation_id, texto_anuncio, "", post.public_metrics['like_count'], post.public_metrics['retweet_count']])

            # 2. Buscamos las respuestas a este anuncio específico
            query_resp = f"conversation_id:{post.conversation_id} -from:{username} lang:es"
            respuestas = client.search_recent_tweets(
                query=query_resp,
                max_results=30, # Subimos a 30 para tener más muestra
                tweet_fields=['created_at', 'text', 'public_metrics', 'conversation_id']
            )

            if respuestas.data:
                print(f"   ✅ Capturando {len(respuestas.data)} reacciones...")
                for resp in respuestas.data:
                    texto_u = resp.text.replace('\n', ' ')
                    writer.writerow([
                        'REACCION', 
                        resp.created_at, 
                        resp.conversation_id, 
                        texto_u, 
                        texto_anuncio, # <--- AQUÍ VINCULAMOS LA RESPUESTA CON EL EVENTO
                        resp.public_metrics['like_count'], 
                        resp.public_metrics['retweet_count']
                    ])
            else:
                print("   ℹ️ Sin reacciones recientes.")
            
            time.sleep(1) # Respetamos el rate limit de la API

    print(f"\n✨ Dataset actualizado: {csv_filename}")

if __name__ == "__main__":
    recolectar_conversaciones()
