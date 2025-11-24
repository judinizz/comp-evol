import random
import pickle
import pandas as pd
import numpy as np
from math import exp

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

class ACO:
    def __init__(self, matriz_distancias, num_formigas, num_iteracoes, alpha=1.0, beta=2.0, 
                 evaporacao=0.5, Q=100, elite_weight=2.0):
        self.matriz_distancias = np.array(matriz_distancias)
        self.num_cidades = len(matriz_distancias)
        self.num_formigas = num_formigas
        self.num_iteracoes = num_iteracoes
        self.alpha = alpha
        self.beta = beta
        self.evaporacao = evaporacao
        self.Q = Q
        self.elite_weight = elite_weight

        self.feromonios = np.ones((self.num_cidades, self.num_cidades)) * 0.1
        
        self.visibilidade = np.zeros((self.num_cidades, self.num_cidades))
        for i in range(self.num_cidades):
            for j in range(self.num_cidades):
                if i != j and self.matriz_distancias[i][j] > 0:
                    self.visibilidade[i][j] = 1.0 / self.matriz_distancias[i][j]
        
        self.melhor_rota_global = None
        self.melhor_custo_global = float('inf')
        self.historico_custos = []
    
    def calcular_probabilidades(self, cidade_atual, cidades_nao_visitadas):
        probabilidades = []
        denominador = 0
    
        for cidade in cidades_nao_visitadas:
            feromonio = self.feromonios[cidade_atual][cidade] ** self.alpha
            visibilidade = self.visibilidade[cidade_atual][cidade] ** self.beta
            denominador += feromonio * visibilidade
        
        if denominador == 0:
            return [1.0 / len(cidades_nao_visitadas)] * len(cidades_nao_visitadas)
        
        for cidade in cidades_nao_visitadas:
            feromonio = self.feromonios[cidade_atual][cidade] ** self.alpha
            visibilidade = self.visibilidade[cidade_atual][cidade] ** self.beta
            prob = (feromonio * visibilidade) / denominador
            probabilidades.append(prob)
        
        return probabilidades
    
    def escolher_proxima_cidade(self, cidade_atual, cidades_nao_visitadas):
        if not cidades_nao_visitadas:
            return None
        
        probabilidades = self.calcular_probabilidades(cidade_atual, cidades_nao_visitadas)
        
        rand = random.random()
        probabilidade_acumulada = 0
        
        for i, prob in enumerate(probabilidades):
            probabilidade_acumulada += prob
            if rand <= probabilidade_acumulada:
                return cidades_nao_visitadas[i]
        
        return cidades_nao_visitadas[-1]
    
    def construir_rota(self, cidade_inicial):
        rota = [cidade_inicial]
        cidades_nao_visitadas = list(range(self.num_cidades))
        cidades_nao_visitadas.remove(cidade_inicial)
        
        cidade_atual = cidade_inicial
        
        while cidades_nao_visitadas:
            proxima_cidade = self.escolher_proxima_cidade(cidade_atual, cidades_nao_visitadas)
            rota.append(proxima_cidade)
            cidades_nao_visitadas.remove(proxima_cidade)
            cidade_atual = proxima_cidade
        
        return rota
    
    def atualizar_feromonios(self, rotas_formigas, custos_formigas):
        self.feromonios *= (1 - self.evaporacao)

        for i, rota in enumerate(rotas_formigas):
            custo = custos_formigas[i]
            deposicao = self.Q / custo

            for j in range(len(rota)):
                cidade_origem = rota[j]
                cidade_destino = rota[(j + 1) % len(rota)]  # Volta ao início
                self.feromonios[cidade_origem][cidade_destino] += deposicao
                self.feromonios[cidade_destino][cidade_origem] += deposicao  # Matriz simétrica
        
        if self.melhor_rota_global is not None:
            deposicao_elite = self.elite_weight * self.Q / self.melhor_custo_global
            rota = self.melhor_rota_global
            
            for j in range(len(rota)):
                cidade_origem = rota[j]
                cidade_destino = rota[(j + 1) % len(rota)]
                self.feromonios[cidade_origem][cidade_destino] += deposicao_elite
                self.feromonios[cidade_destino][cidade_origem] += deposicao_elite
    
    def executar(self, cidade_inicial=0):
        print(f"Iniciando ACO com {self.num_formigas} formigas, {self.num_iteracoes} iterações")
        print(f"Parâmetros: α={self.alpha}, β={self.beta}, ρ={self.evaporacao}")
        
        for iteracao in range(self.num_iteracoes):
            rotas_formigas = []
            custos_formigas = []
            
            for formiga in range(self.num_formigas):
                rota = self.construir_rota(cidade_inicial)
                custo = calcular_custo_rota(rota, self.matriz_distancias)
                
                rotas_formigas.append(rota)
                custos_formigas.append(custo)
                
                if custo < self.melhor_custo_global:
                    self.melhor_custo_global = custo
                    self.melhor_rota_global = rota[:]
                    print(f"Iteração {iteracao}, Formiga {formiga}: Nova melhor solução! Custo = {custo:.2f}")
            
            self.atualizar_feromonios(rotas_formigas, custos_formigas)
            
            melhor_custo_iteracao = min(custos_formigas)
            custo_medio_iteracao = sum(custos_formigas) / len(custos_formigas)
            self.historico_custos.append({
                'iteracao': iteracao,
                'melhor_custo': melhor_custo_iteracao,
                'custo_medio': custo_medio_iteracao,
                'melhor_global': self.melhor_custo_global
            })
            
            if iteracao % 50 == 0:
                print(f"Iteração {iteracao}: Melhor da iteração = {melhor_custo_iteracao:.2f}, "
                      f"Melhor global = {self.melhor_custo_global:.2f}")
        
        return self.melhor_rota_global, self.melhor_custo_global, self.historico_custos

def imprimir_resultado(melhor_rota, melhor_custo, bares_df, historico_custos):
    print("RESULTADO DO ALGORITMO DE COLÔNIA DE FORMIGAS (ACO)")
    print("="*50)
    print(f"Melhor custo encontrado: {melhor_custo:.2f} km")
    print(f"Número de iterações: {len(historico_custos)}")
    
    if historico_custos:
        custo_inicial = historico_custos[0]['custo_medio']
        melhoria = ((custo_inicial - melhor_custo) / custo_inicial * 100)
        print(f"Melhoria total: {melhoria:.1f}%")
    
    print(f"\nMelhor rota encontrada ({len(melhor_rota)} bares):")
    for i, idx_bar in enumerate(melhor_rota):
        nome_bar = bares_df.iloc[idx_bar]['Nome do Buteco']
        print(f"{i+1:2d}. {nome_bar}")
    
    nome_inicial = bares_df.iloc[melhor_rota[0]]['Nome do Buteco']
    print(f"{len(melhor_rota)+1:2d}. {nome_inicial} (retorno)")

if __name__ == "__main__":
    bares_df, matriz_distancias, matriz_tempos = carregar_dados()
    
    print(f"Dados carregados: {len(bares_df)} bares")
    
    NUM_FORMIGAS = 20
    NUM_ITERACOES = 200
    ALPHA = 1.0  # Importância do feromônio
    BETA = 2.0   # Importância da distância
    EVAPORACAO = 0.5  # Taxa de evaporação
    Q = 100      # Constante para deposição
    ELITE_WEIGHT = 2.0  # Peso do elitismo
    
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

    print(f"\nExecutando Algoritmo de Colônia de Formigas...")
    print(f"Parâmetros: {NUM_FORMIGAS} formigas, {NUM_ITERACOES} iterações")
    
    aco = ACO(
        matriz_distancias=matriz_distancias,
        num_formigas=NUM_FORMIGAS,
        num_iteracoes=NUM_ITERACOES,
        alpha=ALPHA,
        beta=BETA,
        evaporacao=EVAPORACAO,
        Q=Q,
        elite_weight=ELITE_WEIGHT
    )
    
    melhor_rota, melhor_custo, historico = aco.executar(cidade_inicial)
    
    imprimir_resultado(melhor_rota, melhor_custo, bares_df, historico)