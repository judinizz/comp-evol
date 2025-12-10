"""
Algoritmo de Kruskal para Árvore Geradora Mínima (AGM)

Este módulo implementa o algoritmo de Kruskal para encontrar a Árvore Geradora Mínima
de um grafo representado por uma matriz de distâncias. A AGM conecta todos os vértices
com o menor custo total possível, sem formar ciclos.

O algoritmo utiliza a estrutura Union-Find (Disjoint Set) para detectar ciclos eficientemente.
"""


class UnionFind:
    """
    Estrutura de dados Union-Find (Disjoint Set)

    Utilizada para rastrear conjuntos disjuntos e detectar ciclos no grafo.
    Implementa otimizações de compressão de caminho e união por rank.
    """

    def __init__(self, n):
        """
        Inicializa a estrutura Union-Find

        Args:
            n (int): Número de elementos (vértices)
        """
        self.parent = list(range(n))  # Cada elemento é seu próprio pai inicialmente
        self.rank = [0] * n  # Rank para otimização de união

    def find(self, x):
        """
        Encontra o representante (raiz) do conjunto de x
        Implementa compressão de caminho para otimização

        Args:
            x (int): Elemento a ser buscado

        Returns:
            int: Representante do conjunto
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Compressão de caminho
        return self.parent[x]

    def union(self, x, y):
        """
        Une os conjuntos que contêm x e y
        Implementa união por rank para manter a árvore balanceada

        Args:
            x (int): Primeiro elemento
            y (int): Segundo elemento

        Returns:
            bool: True se os conjuntos foram unidos, False se já estavam no mesmo conjunto
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Já estão no mesmo conjunto (formaria ciclo)

        # União por rank: anexa a árvore menor à maior
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True


def kruskal(matriz_distancias):
    """
    Implementa o algoritmo de Kruskal para encontrar a Árvore Geradora Mínima

    Passos do algoritmo:
    1. Criar lista de todas as arestas com seus pesos
    2. Ordenar arestas por peso (crescente)
    3. Para cada aresta (menor para maior):
        - Se não formar ciclo, adicionar à AGM
        - Parar quando tiver (n-1) arestas

    Args:
        matriz_distancias (list): Matriz n x n com distâncias entre vértices
                                  matriz_distancias[i][j] = distância de i para j

    Returns:
        tuple: (arestas_agm, custo_total)
            - arestas_agm: Lista de tuplas (vertice_i, vertice_j, peso)
            - custo_total: Soma total dos pesos das arestas na AGM
    """
    n = len(matriz_distancias)

    # Passo 1: Criar lista de arestas
    # Formato: (peso, vertice_i, vertice_j)
    arestas = []
    for i in range(n):
        for j in range(i + 1, n):  # Apenas metade da matriz (grafo não-direcionado)
            if i != j:
                peso = matriz_distancias[i][j]
                arestas.append((peso, i, j))

    # Passo 2: Ordenar arestas por peso (crescente)
    arestas.sort()

    # Passo 3: Inicializar Union-Find e resultado
    uf = UnionFind(n)
    arestas_agm = []
    custo_total = 0.0

    # Passo 4: Processar arestas em ordem crescente de peso
    for peso, i, j in arestas:
        # Se adicionar esta aresta não formar ciclo
        if uf.union(i, j):
            arestas_agm.append((i, j, peso))
            custo_total += peso

            # AGM completa tem exatamente (n-1) arestas
            if len(arestas_agm) == n - 1:
                break

    return arestas_agm, custo_total


def kruskal_com_detalhes(matriz_distancias, df_bares=None):
    """
    Executa Kruskal com informações detalhadas sobre o processo

    Args:
        matriz_distancias (list): Matriz de distâncias
        df_bares (DataFrame, optional): DataFrame com informações dos bares

    Returns:
        dict: Dicionário com informações detalhadas da AGM
    """
    n = len(matriz_distancias)
    arestas_agm, custo_total = kruskal(matriz_distancias)

    resultado = {
        "num_vertices": n,
        "num_arestas": len(arestas_agm),
        "custo_total": custo_total,
        "arestas": [],
    }

    # Adicionar informações detalhadas de cada aresta
    for i, j, peso in arestas_agm:
        aresta_info = {"vertice_origem": i, "vertice_destino": j, "peso": peso}

        # Se temos informações dos bares, adicionar nomes
        if df_bares is not None:
            aresta_info["bar_origem"] = df_bares.iloc[i]["Nome do Buteco"]
            aresta_info["bar_destino"] = df_bares.iloc[j]["Nome do Buteco"]

        resultado["arestas"].append(aresta_info)

    return resultado


def calcular_grau_vertices(arestas_agm, n):
    """
    Calcula o grau (número de arestas conectadas) de cada vértice na AGM

    Args:
        arestas_agm (list): Lista de arestas da AGM
        n (int): Número de vértices

    Returns:
        list: Lista com o grau de cada vértice
    """
    graus = [0] * n

    for i, j, _ in arestas_agm:
        graus[i] += 1
        graus[j] += 1

    return graus


def visualizar_agm(arestas_agm, df_bares=None):
    """
    Gera uma representação textual da AGM

    Args:
        arestas_agm (list): Lista de arestas da AGM
        df_bares (DataFrame, optional): DataFrame com informações dos bares

    Returns:
        str: Representação textual da AGM
    """
    linhas = []
    linhas.append("=" * 80)
    linhas.append("ÁRVORE GERADORA MÍNIMA (AGM) - Algoritmo de Kruskal")
    linhas.append("=" * 80)
    linhas.append(f"\nTotal de arestas: {len(arestas_agm)}")

    custo_total = sum(peso for _, _, peso in arestas_agm)
    linhas.append(f"Custo total: {custo_total:.2f}")
    linhas.append("\nArestas da AGM:")
    linhas.append("-" * 80)

    for idx, (i, j, peso) in enumerate(arestas_agm, 1):
        if df_bares is not None:
            nome_i = df_bares.iloc[i]["Nome do Buteco"]
            nome_j = df_bares.iloc[j]["Nome do Buteco"]
            linhas.append(
                f"{idx:3d}. [{i:3d}] {nome_i:30s} <---> [{j:3d}] {nome_j:30s} : {peso:8.2f}"
            )
        else:
            linhas.append(
                f"{idx:3d}. Vértice {i:3d} <---> Vértice {j:3d} : Peso {peso:8.2f}"
            )

    linhas.append("=" * 80)

    return "\n".join(linhas)


def comparar_com_tsp(custo_agm, custo_tsp):
    """
    Compara o custo da AGM com uma solução TSP

    A AGM fornece um limite inferior para o TSP, pois:
    - AGM conecta todos os vértices com custo mínimo
    - TSP precisa visitar todos e retornar (ciclo)
    - Custo TSP >= Custo AGM

    Args:
        custo_agm (float): Custo total da AGM
        custo_tsp (float): Custo da solução TSP

    Returns:
        dict: Informações da comparação
    """
    diferenca = custo_tsp - custo_agm
    percentual = (diferenca / custo_agm) * 100 if custo_agm > 0 else 0

    return {
        "custo_agm": custo_agm,
        "custo_tsp": custo_tsp,
        "diferenca": diferenca,
        "percentual_acima": percentual,
        "qualidade": "Excelente"
        if percentual < 20
        else "Boa"
        if percentual < 40
        else "Razoável",
    }


if __name__ == "__main__":
    """
    Exemplo de uso do algoritmo de Kruskal
    """
    import pickle

    import pandas as pd

    # Carregar dados
    print("🔄 Carregando dados...")
    df = pd.read_csv("data/bares.csv")

    with open("data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)

    print(f"✅ {len(df)} bares carregados")
    print(f"✅ Matriz de distâncias: {len(distancias)}x{len(distancias[0])}")

    # Executar Kruskal
    print("\n🌳 Executando algoritmo de Kruskal...")
    arestas_agm, custo_total = kruskal(distancias)

    print("\n✅ AGM calculada com sucesso!")
    print(f"   Número de arestas: {len(arestas_agm)}")
    print(f"   Custo total: {custo_total:.2f}")

    # Calcular graus
    graus = calcular_grau_vertices(arestas_agm, len(df))
    grau_max = max(graus)
    grau_medio = sum(graus) / len(graus)

    print("\n📊 Estatísticas dos vértices:")
    print(f"   Grau máximo: {grau_max}")
    print(f"   Grau médio: {grau_medio:.2f}")
    print(f"   Vértices com grau 1 (folhas): {graus.count(1)}")

    # Mostrar primeiras 10 arestas
    print("\n🔗 Primeiras 10 arestas da AGM:")
    for idx, (i, j, peso) in enumerate(arestas_agm[:10], 1):
        nome_i = df.iloc[i]["Nome do Buteco"]
        nome_j = df.iloc[j]["Nome do Buteco"]
        print(f"   {idx:2d}. {nome_i:30s} <---> {nome_j:30s} : {peso:8.2f}")

    # Salvar resultado completo
    print("\n💾 Salvando visualização completa...")
    with open("output/agm_kruskal.txt", "w", encoding="utf-8") as f:
        f.write(visualizar_agm(arestas_agm, df))

    print("✅ Resultado salvo em output/agm_kruskal.txt")
