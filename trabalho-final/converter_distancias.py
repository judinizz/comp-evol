import pandas as pd
import numpy as np

def converter_km_para_minutos(distancia_km, velocidade_kmh=18):
    try:
        distancia_km = float(distancia_km)
    except (ValueError, TypeError):
        print(f"Erro ao converter valor: {distancia_km}")
        return 0
    
    if distancia_km == 0:
        return 0
    
    tempo_horas = distancia_km / velocidade_kmh
    
    tempo_minutos = tempo_horas * 60
    
    return round(tempo_minutos, 2)

def main():   
    try:
        matriz_km = pd.read_csv("data/matriz_distancias.csv", index_col=0)
    except FileNotFoundError:
        try:
            matriz_km = pd.read_csv(r"c:\Users\dtiDigital\Desktop\UFMG\Comp Evl\comp-evol\Trabalho Final\data\matriz_distancias.csv", 
                                   index_col=0)
        except FileNotFoundError:
            print("Erro: Arquivo matriz_distancias.csv não encontrado!")
            return
    
    print(f"Matriz carregada com dimensões: {matriz_km.shape}")
    print(f"Estabelecimentos: {len(matriz_km.columns)}")
    
    matriz_km_numeric = matriz_km.apply(pd.to_numeric, errors='coerce')
    
    nan_count = matriz_km_numeric.isna().sum().sum()
    if nan_count > 0:
        print(f"Atenção: {nan_count} valores não puderam ser convertidos para números")
        matriz_km_numeric = matriz_km_numeric.fillna(0)
    
    matriz_minutos = matriz_km_numeric.copy()
    
    matriz_minutos = (matriz_km_numeric / 18) * 60
    matriz_minutos = matriz_minutos.round(2)
    
    for nome_bar in matriz_minutos.index:
        if nome_bar in matriz_minutos.columns:
            matriz_minutos.loc[nome_bar, nome_bar] = 0.0
    
    arquivo_csv = "data/matriz_tempos_minutos.csv"
    matriz_minutos.to_csv(arquivo_csv)
    print(f"Matriz CSV salva em: {arquivo_csv}")
    
    arquivo_pkl = "data/matriz_tempos_minutos.pkl"
    matriz_minutos.to_pickle(arquivo_pkl)
    print(f"Matriz PKL salva em: {arquivo_pkl}")


if __name__ == "__main__":
    main()