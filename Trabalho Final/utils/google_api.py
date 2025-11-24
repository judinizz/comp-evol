import googlemaps
import pandas as pd
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

def converter_coordenada(coord_str):
    if isinstance(coord_str, str):
        return float(coord_str.replace('.', '')) / 1000000
    return float(coord_str)

def obter_matriz_distancia(df, api_key, cache_path="../data/distancias.pkl"):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    gmaps = googlemaps.Client(key=api_key)
    n = len(df)
    distancias = [[0]*n for _ in range(n)]
    tempos = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i+1, n):
            lat_i = converter_coordenada(df.loc[i,"Latitude"])
            lon_i = converter_coordenada(df.loc[i,"Longitude"])
            lat_j = converter_coordenada(df.loc[j,"Latitude"])
            lon_j = converter_coordenada(df.loc[j,"Longitude"])
            
            print(f"Processando {i} -> {j}: ({lat_i}, {lon_i}) -> ({lat_j}, {lon_j})")
            
            res = gmaps.distance_matrix(
                origins=[(lat_i, lon_i)],
                destinations=[(lat_j, lon_j)],
                mode="driving"
            )
            
            print(f"Resposta da API: {res}")
            
            if res["status"] != "OK":
                print(f"Erro na API: {res['status']}")
                continue
                
            element = res["rows"][0]["elements"][0]
            
            if element["status"] != "OK":
                print(f"Erro no elemento: {element['status']}")
                if "error_message" in element:
                    print(f"Mensagem de erro: {element['error_message']}")
                continue
            
            if "distance" not in element or "duration" not in element:
                print(f"Resposta incompleta: {element}")
                continue
                
            distancias[i][j] = distancias[j][i] = element["distance"]["value"] / 1000
            tempos[i][j] = tempos[j][i] = element["duration"]["value"] / 60

    with open(cache_path, "wb") as f:
        pickle.dump((distancias, tempos), f)

    return distancias, tempos

def salvar_matriz_csv(df, cache_path="../data/distancias.pkl", output_path="../data/matriz_distancias.csv"):
    if not os.path.exists(cache_path):
        print(f"Arquivo {cache_path} não encontrado!")
        return
    
    with open(cache_path, "rb") as f:
        distancias, tempos = pickle.load(f)
    
    nomes_bares = df['Nome do Buteco'].tolist()
    
    df_distancias = pd.DataFrame(distancias, index=nomes_bares, columns=nomes_bares)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_distancias.to_csv(output_path, encoding='utf-8')
    
    print(f"Matriz de distâncias salva em: {output_path}")
    print(f"Dimensões: {len(nomes_bares)} x {len(nomes_bares)}")
    
    return df_distancias

bares_df = pd.read_csv("../database/bares.csv")

print("Carregando matriz de distâncias do cache e salvando em CSV...")
matriz_distancias = salvar_matriz_csv(bares_df)

if matriz_distancias is not None:
    print("\nPrimeiras 5x5 distâncias (em km):")
    print(matriz_distancias.iloc[:5, :5])