import tweepy
import csv
import os
import time
from config_twitter import BEARER_TOKEN

# ==============================================================================
# CONFIGURACIÓN PARA DATASET DE CULTURA
# ==============================================================================
# Lista de cuentas clave para la actividad cultural en Buenos Aires
CUENTAS_ECOSISTEMA = [
    'FestivalesGCBA', 
    'datacultura',  
    'TeatroColon', 
    'elrecoleta', 
    'CCKirchner',
    'gcba',
    'gabiricardes'
]
META_POR_CUENTA = 700          # Intentar bajar 700 interacciones por cuenta
CSV_SALIDA = "dataset_recolectado_CULTURA.csv"
# ==============================================================================

def obtener_ids_existentes():
    if not os.path.isfile(CSV_SALIDA): return set()
    ids = set()
    try:
        with open(CSV_SALIDA, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'id_tuit' in row: ids.add(row['id_tuit'])
    except: pass
    return ids

def recolector_masivo_cultura():
    client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)
    ids_viejos = obtener_ids_existentes()
    
    print(f"🚀 INICIANDO RECOLECCIÓN CULTURA (Meta: >5000 registros)")
    print(f"📋 Ecosistema Cultural: {len(CUENTAS_ECOSISTEMA)} cuentas")

    if not os.path.isfile(CSV_SALIDA):
        with open(CSV_SALIDA, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['tipo', 'fecha', 'id_tuit', 'id_conversacion', 'cuenta_origen', 'texto', 'referencia_anuncio', 'likes', 'rts'])

    for cuenta in CUENTAS_ECOSISTEMA:
        print(f"\n--- 🎨 Procesando @{cuenta} ---")
        
        try:
            # 1. ANUNCIOS (Hilos Oficiales)
            posts = client.search_recent_tweets(
                query=f"from:{cuenta} -is:retweet",
                max_results=100,
                tweet_fields=['created_at', 'text', 'conversation_id', 'public_metrics']
            )
            
            if posts.data:
                print(f"   📢 Hallados {len(posts.data)} posts oficiales. Buscando respuestas...")
                for post in posts.data:
                    if str(post.id) not in ids_viejos:
                        guardar_fila('ANUNCIO', post, cuenta, "", ids_viejos)
                        bajar_respuestas_masivo(post, cuenta, client, ids_viejos)
            
            # 2. MENCIONES (Público hablando a la cuenta)
            print(f"   🔎 Buscando menciones de usuarios a @{cuenta} (Sin filtros)...")
            query_menc = f"(@{cuenta}) -from:{cuenta} -is:retweet lang:es"
            
            count_menc = 0
            for page in tweepy.Paginator(client.search_recent_tweets, 
                                         query=query_menc,
                                         max_results=100, 
                                         tweet_fields=['created_at', 'text', 'conversation_id', 'public_metrics'],
                                         limit=7): 
                if page.data:
                    for tweet in page.data:
                        if str(tweet.id) not in ids_viejos:
                            guardar_fila('MENCION_DIRECTA', tweet, cuenta, "", ids_viejos)
                            count_menc += 1
                if count_menc >= META_POR_CUENTA: break
            print(f"   ✅ {count_menc} menciones guardadas.")

        except Exception as e:
            print(f"   ⚠️ Error con @{cuenta}: {e}")
            continue

def bajar_respuestas_masivo(post, cuenta, client, ids_viejos):
    query_resp = f"conversation_id:{post.conversation_id} -from:{cuenta} lang:es"
    try:
        resps = client.search_recent_tweets(query=query_resp, max_results=100, tweet_fields=['created_at', 'text', 'public_metrics'])
        if resps.data:
            for r in resps.data:
                if str(r.id) not in ids_viejos:
                    guardar_fila('REACCION', r, cuenta, post.text, ids_viejos)
    except: pass

def guardar_fila(tipo, tweet, cuenta, ref, ids_viejos):
    texto = tweet.text.replace('\n', ' ').replace('\r', '')
    ref_texto = ref.replace('\n', ' ').replace('\r', '') if ref else ""
    with open(CSV_SALIDA, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([tipo, tweet.created_at, tweet.id, tweet.conversation_id, cuenta, texto, ref_texto, tweet.public_metrics['like_count'], tweet.public_metrics['retweet_count']])
    ids_viejos.add(str(tweet.id))

if __name__ == "__main__":
    recolector_masivo_cultura()
