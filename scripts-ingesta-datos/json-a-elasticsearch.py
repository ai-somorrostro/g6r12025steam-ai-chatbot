import json
import ndjson
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from tqdm import tqdm

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX")
DATASET_PATH = os.getenv("DATASET_PATH", "data/steam_games_data_vect.ndjson")

es = Elasticsearch(ELASTIC_URL)

def cargar_a_elasticsearch():
    print(f"📥 Cargando dataset desde {DATASET_PATH}")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        datos = ndjson.load(f)

    print(f"📤 Ingresando {len(datos)} documentos al índice '{ELASTIC_INDEX}'...")

    for doc in tqdm(datos):
        es.index(index=ELASTIC_INDEX, document=doc)

    print("✅ Carga completada")

if __name__ == "__main__":
    cargar_a_elasticsearch()
