import random
import pickle
import pandas as pd
from copy import deepcopy

def carregar_dados():
    try:
        bares_df = pd.read_csv("data/bares.csv")
        with open("data/distancias.pkl", "rb") as f:
            distancias, tempos = pickle.load(f)
    except FileNotFoundError:
        bares_df = pd.read_csv("../data/bares.csv")
        with open("../data/distancias.pkl", "rb") as f:
            distancias, tempos = pickle.load(f)
    
    return bares_df, distancias, tempos

def calcular_custo_rota(rota, matriz_distancias):
    custo_total = 0
    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]
        custo_total += matriz_distancias[origem][destino]
    
    custo_total += matriz_distancias[rota[-1]][rota[0]]
    
    return custo_total

def gerar_vizinhos_2opt(rota):
    vizinhos = []
    n = len(rota)
    
    for i in range(n - 1):
        for j in range(i + 2, n):
            novo_vizinho = rota[:i+1] + rota[i+1:j+1][::-1] + rota[j+1:]
            vizinhos.append(novo_vizinho)
    
    return vizinhos

def gerar_vizinhos_swap(rota):
    vizinhos = []
    n = len(rota)
    
    for i in range(n):
        for j in range(i + 1, n):
            novo_vizinho = rota[:]
            novo_vizinho[i], novo_vizinho[j] = novo_vizinho[j], novo_vizinho[i]
            vizinhos.append(novo_vizinho)
    
    return vizinhos

def gerar_vizinhos_insert(rota):
    vizinhos = []
    n = len(rota)
    
    for i in range(n):
        for j in range(n):
            if i != j:
                novo_vizinho = rota[:]
                elemento = novo_vizinho.pop(i)
                novo_vizinho.insert(j, elemento)
                vizinhos.append(novo_vizinho)
    
    return vizinhos

def tabu_search_classico(matriz_distancias, num_cidades, 
                        max_iteracoes=1000, tamanho_lista_tabu=50, 
                        cidade_inicial=0, usar_todos_movimentos=True):

    cidades_restantes = [i for i in range(num_cidades) if i != cidade_inicial]
    random.shuffle(cidades_restantes)
    solucao_atual = [cidade_inicial] + cidades_restantes
    
    melhor_solucao = solucao_atual[:]
    custo_atual = calcular_custo_rota(solucao_atual, matriz_distancias)
    melhor_custo = custo_atual
    
    lista_tabu = []
    historico_custos = [custo_atual]
    
    print(f"Solução inicial: custo = {custo_atual:.2f}")
    
    for iteracao in range(max_iteracoes):
        if usar_todos_movimentos:
            vizinhos = []
            vizinhos.extend(gerar_vizinhos_2opt(solucao_atual))
            vizinhos.extend(gerar_vizinhos_swap(solucao_atual))
            vizinhos.extend(gerar_vizinhos_insert(solucao_atual))
        else:
            vizinhos = gerar_vizinhos_2opt(solucao_atual)
        
        melhor_vizinho = None
        melhor_custo_vizinho = float('inf')
        melhor_movimento = None
        
        for vizinho in vizinhos:
            custo_vizinho = calcular_custo_rota(vizinho, matriz_distancias)
            movimento = tuple(sorted([tuple(solucao_atual), tuple(vizinho)]))
            
            if custo_vizinho < melhor_custo:
                melhor_vizinho = vizinho
                melhor_custo_vizinho = custo_vizinho
                melhor_movimento = movimento
                break
            
            if movimento not in lista_tabu:
                if custo_vizinho < melhor_custo_vizinho:
                    melhor_vizinho = vizinho
                    melhor_custo_vizinho = custo_vizinho
                    melhor_movimento = movimento
        

        if melhor_vizinho is None:
            print(f"Não há mais movimentos válidos na iteração {iteracao}")
            break
        
        solucao_atual = melhor_vizinho
        custo_atual = melhor_custo_vizinho
        
        if custo_atual < melhor_custo:
            melhor_solucao = solucao_atual[:]
            melhor_custo = custo_atual
            print(f"Iteração {iteracao}: Nova melhor solução encontrada! Custo = {melhor_custo:.2f}")
        
        if melhor_movimento:
            lista_tabu.append(melhor_movimento)
            if len(lista_tabu) > tamanho_lista_tabu:
                lista_tabu.pop(0)
        
        historico_custos.append(custo_atual)
        
        if iteracao % 100 == 0 and iteracao > 0:
            print(f"Iteração {iteracao}: Custo atual = {custo_atual:.2f}, Melhor = {melhor_custo:.2f}")
    
    return melhor_solucao, melhor_custo, historico_custos

def imprimir_resultado(melhor_rota, melhor_custo, bares_df, historico_custos):
    print("RESULTADO DO TABU SEARCH CLÁSSICO")
    print("="*50)
    print(f"Melhor custo encontrado: {melhor_custo:.2f} km")
    print(f"Número de iterações: {len(historico_custos)}")
    print(f"Melhoria total: {((historico_custos[0] - melhor_custo) / historico_custos[0] * 100):.1f}%")
    
    print(f"\nMelhor rota encontrada ({len(melhor_rota)} bares):")
    for i, idx_bar in enumerate(melhor_rota):
        nome_bar = bares_df.iloc[idx_bar]['Nome do Buteco']
        print(f"{i+1:2d}. {nome_bar}")
    
    nome_inicial = bares_df.iloc[melhor_rota[0]]['Nome do Buteco']
    print(f"{len(melhor_rota)+1:2d}. {nome_inicial} (retorno)")

if __name__ == "__main__":
    print("Carregando dados...")
    bares_df, matriz_distancias, matriz_tempos = carregar_dados()
    
    print(f"Dados carregados: {len(bares_df)} bares")
    MAX_ITERACOES = 500
    TAMANHO_LISTA_TABU = 50

    print("\nEscolha o bar inicial:")
    print("0. Escolha automática (aleatória)")
    for i, row in bares_df.iterrows():
        print(f"{i+1}. {row['Nome do Buteco']}")
    
    while True:
        try:
            escolha = int(input(f"\nDigite o número (0-{len(bares_df)}): "))
            if 0 <= escolha <= len(bares_df):
                cidade_inicial = escolha - 1 if escolha > 0 else random.randint(0, len(bares_df)-1)
                break
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")
    
    if escolha == 0:
        print(f"Bar inicial escolhido automaticamente: {bares_df.iloc[cidade_inicial]['Nome do Buteco']}")
    else:
        print(f"Bar inicial escolhido: {bares_df.iloc[cidade_inicial]['Nome do Buteco']}")
    
    print(f"\nExecutando Tabu Search...")
    print(f"Parâmetros: max_iter={MAX_ITERACOES}, tabu_size={TAMANHO_LISTA_TABU}")
    
    melhor_rota, melhor_custo, historico = tabu_search_classico(
        matriz_distancias=matriz_distancias,
        num_cidades=len(bares_df),
        max_iteracoes=MAX_ITERACOES,
        tamanho_lista_tabu=TAMANHO_LISTA_TABU,
        cidade_inicial=cidade_inicial,
        usar_todos_movimentos=True
    )

    imprimir_resultado(melhor_rota, melhor_custo, bares_df, historico)