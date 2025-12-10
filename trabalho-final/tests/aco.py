"""
Ant Colony Optimization (ACO) para TSP

Implementação do algoritmo de colônia de formigas para o problema
do caixeiro viajante, seguindo o mesmo padrão dos testes de
Kruskal, Bellmore-Nemhauser e Tabu Search.
"""

import random

import numpy as np


def calcular_custo_rota(rota, matriz_distancias):
    """
    Calcula o custo total de uma rota (incluindo retorno ao início)

    Args:
        rota: Lista com índices dos bares na ordem da rota
        matriz_distancias: Matriz de distâncias entre bares

    Returns:
        Custo total da rota em km
    """
    custo_total = 0
    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]
        custo_total += matriz_distancias[origem][destino]

    # Adicionar retorno ao início
    custo_total += matriz_distancias[rota[-1]][rota[0]]

    return custo_total


class ACO:
    """
    Algoritmo de Colônia de Formigas (Ant Colony Optimization)

    Parâmetros:
        - alpha: importância do feromônio (padrão: 1.0)
        - beta: importância da distância (padrão: 2.0)
        - evaporacao: taxa de evaporação de feromônio (padrão: 0.5)
        - Q: constante para deposição de feromônio (padrão: 100)
        - elite_weight: peso da melhor solução (elitismo) (padrão: 2.0)
    """

    def __init__(
        self,
        matriz_distancias,
        num_formigas,
        num_iteracoes,
        alpha=1.0,
        beta=2.0,
        evaporacao=0.5,
        Q=100,
        elite_weight=2.0,
        verbose=True,
    ):
        self.matriz_distancias = np.array(matriz_distancias)
        self.num_cidades = len(matriz_distancias)
        self.num_formigas = num_formigas
        self.num_iteracoes = num_iteracoes
        self.alpha = alpha
        self.beta = beta
        self.evaporacao = evaporacao
        self.Q = Q
        self.elite_weight = elite_weight
        self.verbose = verbose

        # Inicializar matriz de feromônios com valor pequeno
        self.feromonios = np.ones((self.num_cidades, self.num_cidades)) * 0.1

        # Calcular visibilidade (inverso da distância)
        self.visibilidade = np.zeros((self.num_cidades, self.num_cidades))
        for i in range(self.num_cidades):
            for j in range(self.num_cidades):
                if i != j and self.matriz_distancias[i][j] > 0:
                    self.visibilidade[i][j] = 1.0 / self.matriz_distancias[i][j]

        # Variáveis para rastrear melhor solução
        self.melhor_rota_global = None
        self.melhor_custo_global = float("inf")
        self.historico_custos = []

    def calcular_probabilidades(self, cidade_atual, cidades_nao_visitadas):
        """
        Calcula probabilidades de escolha para cada cidade não visitada

        Probabilidade é proporcional a: (feromônio^alpha) * (visibilidade^beta)
        """
        probabilidades = []
        denominador = 0

        # Calcular denominador (soma de todas as probabilidades não normalizadas)
        for cidade in cidades_nao_visitadas:
            feromonio = self.feromonios[cidade_atual][cidade] ** self.alpha
            visibilidade = self.visibilidade[cidade_atual][cidade] ** self.beta
            denominador += feromonio * visibilidade

        # Se denominador é zero, retornar probabilidades uniformes
        if denominador == 0:
            return [1.0 / len(cidades_nao_visitadas)] * len(cidades_nao_visitadas)

        # Calcular probabilidades normalizadas
        for cidade in cidades_nao_visitadas:
            feromonio = self.feromonios[cidade_atual][cidade] ** self.alpha
            visibilidade = self.visibilidade[cidade_atual][cidade] ** self.beta
            prob = (feromonio * visibilidade) / denominador
            probabilidades.append(prob)

        return probabilidades

    def escolher_proxima_cidade(self, cidade_atual, cidades_nao_visitadas):
        """
        Escolhe próxima cidade usando roleta viciada baseada em probabilidades
        """
        if not cidades_nao_visitadas:
            return None

        probabilidades = self.calcular_probabilidades(
            cidade_atual, cidades_nao_visitadas
        )

        # Roleta viciada
        rand = random.random()
        probabilidade_acumulada = 0

        for i, prob in enumerate(probabilidades):
            probabilidade_acumulada += prob
            if rand <= probabilidade_acumulada:
                return cidades_nao_visitadas[i]

        # Fallback: retornar última cidade
        return cidades_nao_visitadas[-1]

    def construir_rota(self, cidade_inicial):
        """
        Constrói uma rota completa para uma formiga
        """
        rota = [cidade_inicial]
        cidades_nao_visitadas = list(range(self.num_cidades))
        cidades_nao_visitadas.remove(cidade_inicial)

        cidade_atual = cidade_inicial

        while cidades_nao_visitadas:
            proxima_cidade = self.escolher_proxima_cidade(
                cidade_atual, cidades_nao_visitadas
            )
            rota.append(proxima_cidade)
            cidades_nao_visitadas.remove(proxima_cidade)
            cidade_atual = proxima_cidade

        return rota

    def atualizar_feromonios(self, rotas_formigas, custos_formigas):
        """
        Atualiza matriz de feromônios:
        1. Evapora feromônio existente
        2. Deposita novo feromônio baseado nas rotas encontradas
        3. Reforça melhor rota global (elitismo)
        """
        # Evaporação
        self.feromonios *= 1 - self.evaporacao

        # Deposição de feromônio por todas as formigas
        for i, rota in enumerate(rotas_formigas):
            custo = custos_formigas[i]
            deposicao = self.Q / custo

            for j in range(len(rota)):
                cidade_origem = rota[j]
                cidade_destino = rota[(j + 1) % len(rota)]  # Volta ao início
                self.feromonios[cidade_origem][cidade_destino] += deposicao
                self.feromonios[cidade_destino][cidade_origem] += (
                    deposicao  # Matriz simétrica
                )

        # Elitismo: reforçar melhor rota global
        if self.melhor_rota_global is not None:
            deposicao_elite = self.elite_weight * self.Q / self.melhor_custo_global
            rota = self.melhor_rota_global

            for j in range(len(rota)):
                cidade_origem = rota[j]
                cidade_destino = rota[(j + 1) % len(rota)]
                self.feromonios[cidade_origem][cidade_destino] += deposicao_elite
                self.feromonios[cidade_destino][cidade_origem] += deposicao_elite

    def executar(self, cidade_inicial=0):
        """
        Executa o algoritmo ACO

        Returns:
            Tupla (melhor_rota, melhor_custo, historico)
        """
        if self.verbose:
            print(
                f"Iniciando ACO com {self.num_formigas} formigas, {self.num_iteracoes} iterações"
            )
            print(f"Parâmetros: α={self.alpha}, β={self.beta}, ρ={self.evaporacao}")

        for iteracao in range(self.num_iteracoes):
            rotas_formigas = []
            custos_formigas = []

            # Cada formiga constrói uma rota
            for formiga in range(self.num_formigas):
                rota = self.construir_rota(cidade_inicial)
                custo = calcular_custo_rota(rota, self.matriz_distancias)

                rotas_formigas.append(rota)
                custos_formigas.append(custo)

                # Atualizar melhor solução global
                if custo < self.melhor_custo_global:
                    self.melhor_custo_global = custo
                    self.melhor_rota_global = rota[:]
                    if self.verbose:
                        melhoria = (
                            (
                                (self.historico_custos[0]["melhor_global"] - custo)
                                / self.historico_custos[0]["melhor_global"]
                                * 100
                            )
                            if self.historico_custos
                            else 0
                        )
                        print(
                            f"Iteração {iteracao}, Formiga {formiga}: Nova melhor solução! "
                            f"Custo = {custo:.2f} km (melhoria {melhoria:.1f}%)"
                        )

            # Atualizar feromônios
            self.atualizar_feromonios(rotas_formigas, custos_formigas)

            # Registrar histórico
            melhor_custo_iteracao = min(custos_formigas)
            custo_medio_iteracao = sum(custos_formigas) / len(custos_formigas)
            self.historico_custos.append(
                {
                    "iteracao": iteracao,
                    "melhor_custo": melhor_custo_iteracao,
                    "custo_medio": custo_medio_iteracao,
                    "melhor_global": self.melhor_custo_global,
                }
            )

            # Log periódico
            if self.verbose and (iteracao % 50 == 0 or iteracao < 5):
                print(
                    f"Iteração {iteracao}: Melhor da iteração = {melhor_custo_iteracao:.2f}, "
                    f"Melhor global = {self.melhor_custo_global:.2f}"
                )

        if self.verbose:
            print("\n✅ ACO concluído!")
            if self.historico_custos:
                custo_inicial = self.historico_custos[0]["custo_medio"]
                melhoria = (
                    (custo_inicial - self.melhor_custo_global) / custo_inicial * 100
                )
                print(f"   Custo inicial (médio): {custo_inicial:.2f}")
                print(f"   Custo final: {self.melhor_custo_global:.2f}")
                print(f"   Melhoria: {melhoria:.1f}%")
                print(f"   Iterações executadas: {len(self.historico_custos)}")

        return self.melhor_rota_global, self.melhor_custo_global, self.historico_custos


if __name__ == "__main__":
    """Teste do ACO"""
    import pickle

    import pandas as pd

    print("=" * 80)
    print("TESTE: Ant Colony Optimization (ACO)")
    print("=" * 80)

    print("\n🔄 Carregando dados...")
    df = pd.read_csv("data/bares.csv")

    with open("data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)

    print(f"✅ {len(df)} bares carregados\n")

    # Configuração do ACO
    NUM_FORMIGAS = 20
    NUM_ITERACOES = 200
    ALPHA = 1.0  # Importância do feromônio
    BETA = 2.0  # Importância da distância
    EVAPORACAO = 0.5  # Taxa de evaporação
    Q = 100  # Constante para deposição
    ELITE_WEIGHT = 2.0  # Peso do elitismo

    print("Configuração do ACO:")
    print(f"  - Número de formigas: {NUM_FORMIGAS}")
    print(f"  - Número de iterações: {NUM_ITERACOES}")
    print(f"  - Alpha (importância feromônio): {ALPHA}")
    print(f"  - Beta (importância distância): {BETA}")
    print(f"  - Taxa de evaporação: {EVAPORACAO}")
    print(f"  - Elite weight: {ELITE_WEIGHT}")
    print()

    # Criar e executar ACO
    aco = ACO(
        matriz_distancias=distancias,
        num_formigas=NUM_FORMIGAS,
        num_iteracoes=NUM_ITERACOES,
        alpha=ALPHA,
        beta=BETA,
        evaporacao=EVAPORACAO,
        Q=Q,
        elite_weight=ELITE_WEIGHT,
        verbose=True,
    )

    melhor_rota, melhor_custo, historico = aco.executar(cidade_inicial=0)

    print(f"\n🎯 Resultado final: {melhor_custo:.2f} km")

    print("\nPrimeiros 10 bares da rota:")
    for i, idx_bar in enumerate(melhor_rota[:10]):
        nome_bar = df.iloc[idx_bar]["Nome do Buteco"]
        print(f"   {i + 1}. {nome_bar}")

    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)
