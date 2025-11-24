import random
import pickle
import pandas as pd
from copy import deepcopy
from .avalia_rota import avaliar_rota

def carregar_dados():
    bares_df = pd.read_csv("../data/bares.csv")
    with open("../data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)
    
    return bares_df, distancias, tempos

def gerar_vizinhos(rota):
    vizinhos = []
    for i in range(1, len(rota)-1):  
        for j in range(i+1, len(rota)):
            nova = rota[:]
            nova[i], nova[j] = nova[j], nova[i]
            vizinhos.append(nova)
    return vizinhos

def tabu_search(rota_inicial, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha=1.0, beta=20.0, tabu_tam=10, max_iter=100):
    """
    Algoritmo de busca tabu para otimização de rotas de bares
    
    Args:
        rota_inicial: Lista com índices dos bares na ordem inicial
        tempos: Matriz de tempos entre bares (em minutos)
        bares: DataFrame com informações dos bares
        hora_inicial: Hora de início (datetime)
        hora_final: Hora limite (datetime)
        tempo_visita: Tempo de visita por bar (timedelta)
        alpha: Peso para tempo total de viagem
        beta: Peso para soma das notas dos bares
        tabu_tam: Tamanho da lista tabu
        max_iter: Número máximo de iterações
    
    Returns:
        Tupla (melhor_rota, melhor_custo)
    """
    melhor = deepcopy(rota_inicial)
    melhor_custo = avaliar_rota(melhor, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta)
    atual = deepcopy(melhor)
    tabu = []

    print(f"Custo inicial: {melhor_custo}")

    for iteracao in range(max_iter):
        vizinhos = gerar_vizinhos(atual)
        candidatos = []
        
        for v in vizinhos:
            if v not in tabu:
                custo = avaliar_rota(v, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta)
                candidatos.append((v, custo))

        if not candidatos:
            print(f"Não há mais candidatos válidos. Parando na iteração {iteracao}")
            break

        candidatos.sort(key=lambda x: x[1])
        melhor_vizinho, melhor_custo_vizinho = candidatos[0]


        if melhor_custo_vizinho < melhor_custo:
            melhor, melhor_custo = melhor_vizinho, melhor_custo_vizinho
            print(f"Iteração {iteracao}: Nova melhor solução com custo {melhor_custo}")

        tabu.append(deepcopy(melhor_vizinho))
        if len(tabu) > tabu_tam:
            tabu.pop(0)

        atual = melhor_vizinho

    return melhor, melhor_custo


if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    print("Carregando dados...")
    bares_df, distancias, tempos = carregar_dados()
    

    n_bares = min(10, len(bares_df))  
    rota_inicial = list(range(n_bares))  
    
    #config de tempo (precisa ser feito no front)
    hora_inicial = datetime(2024, 11, 12, 18, 0)  
    hora_final = datetime(2024, 11, 12, 23, 0)    
    tempo_visita = timedelta(minutes=30)          # tempo por bar
    
    print(f"Número de bares: {n_bares}")
    print(f"Rota inicial: {rota_inicial}")
    print(f"Horário: {hora_inicial.strftime('%H:%M')} às {hora_final.strftime('%H:%M')}")
    

    melhor_rota, melhor_custo = tabu_search(
        rota_inicial=rota_inicial,
        tempos=tempos,
        bares=bares_df,
        hora_inicial=hora_inicial,
        hora_final=hora_final,
        tempo_visita=tempo_visita,
        alpha=1.0,      # peso do tempo de locomoção
        beta=20.0,      # peso da nota de avaliação
        tabu_tam=10,    # tamanho da lista tabu
        max_iter=50     # max iterações
    )
    
    print(f"\nMelhor rota encontrada: {melhor_rota}")
    print(f"Custo final: {melhor_custo}")
    

    print("\nSequência de bares:")
    for i, idx_bar in enumerate(melhor_rota):
        nome_bar = bares_df.iloc[idx_bar]['Nome do Buteco']
        print(f"{i+1}. {nome_bar}")
