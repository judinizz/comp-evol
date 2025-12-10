"""
Heurística de Bellmore e Nemhauser para TSP

Esta heurística fornece um LIMITE SUPERIOR (teto) para o problema do TSP.
O algoritmo funciona da seguinte forma:

1. Encontra a Árvore Geradora Mínima (AGM) usando Kruskal
2. Duplica todas as arestas da AGM (criando um grafo euleriano)
3. Encontra um circuito euleriano
4. Remove vértices repetidos (atalhos) para formar um circuito hamiltoniano

Teorema: A solução tem custo ≤ 2 × custo_AGM

Este é um limite superior garantido para o TSP.
"""

from tests.kruskal import kruskal


def construir_grafo_adjacencia(arestas_agm, n):
    """
    Constrói lista de adjacência a partir das arestas da AGM

    Args:
        arestas_agm: Lista de tuplas (i, j, peso) da AGM
        n: Número de vértices

    Returns:
        dict: Dicionário de adjacência {vertice: [vizinhos]}
    """
    grafo = {i: [] for i in range(n)}

    for i, j, _ in arestas_agm:
        grafo[i].append(j)
        grafo[j].append(i)

    return grafo


def encontrar_circuito_euleriano(grafo_euleriano, inicio=0):
    """
    Encontra um circuito euleriano usando o algoritmo de Hierholzer

    Args:
        grafo_euleriano: Grafo com todos os vértices de grau par
        inicio: Vértice inicial

    Returns:
        list: Circuito euleriano (sequência de vértices)
    """
    # Criar cópia do grafo para não modificar o original
    from copy import deepcopy

    grafo = deepcopy(grafo_euleriano)

    # Pilha para o algoritmo de Hierholzer
    pilha = [inicio]
    circuito = []

    while pilha:
        v = pilha[-1]

        if grafo[v]:
            # Se tem arestas não visitadas, escolhe uma
            u = grafo[v].pop()
            # Remove aresta reversa
            grafo[u].remove(v)
            pilha.append(u)
        else:
            # Se não tem arestas, adiciona ao circuito
            circuito.append(pilha.pop())

    return circuito[::-1]  # Reverter para ordem correta


def remover_vertices_repetidos(circuito_euleriano):
    """
    Remove vértices repetidos do circuito euleriano (atalhos)
    para formar um circuito hamiltoniano

    Args:
        circuito_euleriano: Circuito com possíveis repetições

    Returns:
        list: Circuito hamiltoniano (cada vértice aparece uma vez)
    """
    visitados = set()
    circuito_hamiltoniano = []

    for v in circuito_euleriano:
        if v not in visitados:
            circuito_hamiltoniano.append(v)
            visitados.add(v)

    return circuito_hamiltoniano


def calcular_custo_circuito(circuito, distancias):
    """
    Calcula o custo total de um circuito

    Args:
        circuito: Lista de vértices do circuito
        distancias: Matriz de distâncias

    Returns:
        float: Custo total do circuito
    """
    custo = 0.0

    for i in range(len(circuito) - 1):
        custo += distancias[circuito[i]][circuito[i + 1]]

    # Adicionar retorno ao início
    if len(circuito) > 0:
        custo += distancias[circuito[-1]][circuito[0]]

    return custo


def bellmore_nemhauser(matriz_distancias):
    """
    Implementa a heurística de Bellmore e Nemhauser para TSP

    Passos:
    1. Encontrar AGM usando Kruskal
    2. Duplicar arestas da AGM (todos os vértices ficam com grau par)
    3. Encontrar circuito euleriano
    4. Remover vértices repetidos (aplicar atalhos)

    Args:
        matriz_distancias: Matriz n x n com distâncias entre vértices

    Returns:
        tuple: (circuito_hamiltoniano, custo_total, custo_agm)
    """
    n = len(matriz_distancias)

    # Passo 1: Encontrar AGM
    arestas_agm, custo_agm = kruskal(matriz_distancias)

    # Passo 2: Duplicar arestas (criar grafo euleriano)
    # Todo vértice terá grau par
    grafo_euleriano = {i: [] for i in range(n)}

    for i, j, _ in arestas_agm:
        # Adicionar aresta nos dois sentidos (duplicar)
        grafo_euleriano[i].append(j)
        grafo_euleriano[j].append(i)
        # Adicionar novamente (duplicar)
        grafo_euleriano[i].append(j)
        grafo_euleriano[j].append(i)

    # Passo 3: Encontrar circuito euleriano
    circuito_euleriano = encontrar_circuito_euleriano(grafo_euleriano)

    # Passo 4: Remover vértices repetidos (atalhos)
    circuito_hamiltoniano = remover_vertices_repetidos(circuito_euleriano)

    # Calcular custo do circuito hamiltoniano
    custo_total = calcular_custo_circuito(circuito_hamiltoniano, matriz_distancias)

    return circuito_hamiltoniano, custo_total, custo_agm


def bellmore_nemhauser_com_detalhes(matriz_distancias, df_bares=None):
    """
    Executa Bellmore-Nemhauser com informações detalhadas

    Args:
        matriz_distancias: Matriz de distâncias
        df_bares: DataFrame com informações dos bares (opcional)

    Returns:
        dict: Dicionário com informações detalhadas
    """
    circuito, custo_total, custo_agm = bellmore_nemhauser(matriz_distancias)

    resultado = {
        "num_vertices": len(matriz_distancias),
        "custo_agm": custo_agm,
        "custo_circuito": custo_total,
        "limite_superior_teorico": 2 * custo_agm,
        "razao_aproximacao": custo_total / custo_agm if custo_agm > 0 else 0,
        "circuito": circuito,
        "tamanho_circuito": len(circuito),
    }

    # Adicionar informações detalhadas se temos dados dos bares
    if df_bares is not None:
        resultado["sequencia_bares"] = [
            df_bares.iloc[i]["Nome do Buteco"] for i in circuito
        ]

    return resultado


def visualizar_bellmore_nemhauser(resultado, df_bares=None):
    """
    Gera uma representação textual do resultado

    Args:
        resultado: Dicionário com resultados de bellmore_nemhauser_com_detalhes
        df_bares: DataFrame com informações dos bares (opcional)

    Returns:
        str: Representação textual
    """
    linhas = []
    linhas.append("=" * 80)
    linhas.append("HEURÍSTICA DE BELLMORE E NEMHAUSER")
    linhas.append("Limite Superior para TSP")
    linhas.append("=" * 80)

    linhas.append("\n📊 Estatísticas:")
    linhas.append(f"   Número de vértices: {resultado['num_vertices']}")
    linhas.append(f"   Tamanho do circuito: {resultado['tamanho_circuito']}")

    linhas.append("\n💰 Custos:")
    linhas.append(f"   Custo AGM: {resultado['custo_agm']:.2f}")
    linhas.append(f"   Custo do circuito: {resultado['custo_circuito']:.2f}")
    linhas.append(
        f"   Limite teórico (2×AGM): {resultado['limite_superior_teorico']:.2f}"
    )

    linhas.append("\n📈 Análise:")
    linhas.append(f"   Razão de aproximação: {resultado['razao_aproximacao']:.4f}")
    diferenca = resultado["custo_circuito"] - resultado["custo_agm"]
    percentual = (
        (diferenca / resultado["custo_agm"] * 100) if resultado["custo_agm"] > 0 else 0
    )
    linhas.append(f"   Diferença para AGM: {diferenca:.2f} ({percentual:.2f}%)")

    linhas.append("\n🎯 Qualidade:")
    if resultado["razao_aproximacao"] <= 1.5:
        qualidade = "EXCELENTE (melhor que esperado!)"
    elif resultado["razao_aproximacao"] <= 2.0:
        qualidade = "BOA (dentro do limite teórico)"
    else:
        qualidade = "Acima do limite teórico esperado"
    linhas.append(f"   {qualidade}")

    linhas.append("\n🗺️ Circuito Hamiltoniano:")
    circuito = resultado["circuito"]

    if df_bares is not None:
        # Mostrar primeiros 10 bares
        for idx in range(min(10, len(circuito))):
            i = circuito[idx]
            nome = df_bares.iloc[i]["Nome do Buteco"]
            linhas.append(f"   {idx + 1:3d}. [{i:3d}] {nome}")

        if len(circuito) > 10:
            linhas.append(f"   ... ({len(circuito) - 10} bares omitidos)")
    else:
        # Mostrar apenas índices
        linhas.append(f"   {circuito[:20]}")
        if len(circuito) > 20:
            linhas.append(f"   ... ({len(circuito) - 20} vértices omitidos)")

    linhas.append("\n" + "=" * 80)

    return "\n".join(linhas)


if __name__ == "__main__":
    """
    Exemplo de uso da heurística de Bellmore e Nemhauser
    """
    import pickle

    import pandas as pd

    # Carregar dados
    print("🔄 Carregando dados...")
    df = pd.read_csv("data/bares.csv")

    with open("data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)

    print(f"✅ {len(df)} bares carregados")

    # Executar Bellmore-Nemhauser
    print("\n🔺 Executando heurística de Bellmore e Nemhauser...")
    resultado = bellmore_nemhauser_com_detalhes(distancias, df)

    print("\n✅ Circuito encontrado!")
    print(f"   Custo AGM: {resultado['custo_agm']:.2f}")
    print(f"   Custo do circuito: {resultado['custo_circuito']:.2f}")
    print(
        f"   Limite superior teórico (2×AGM): {resultado['limite_superior_teorico']:.2f}"
    )
    print(f"   Razão de aproximação: {resultado['razao_aproximacao']:.4f}")

    # Verificar se está dentro do limite teórico
    if resultado["custo_circuito"] <= resultado["limite_superior_teorico"]:
        print("\n✅ Solução está DENTRO do limite teórico!")
    else:
        print("\n⚠️ Solução está ACIMA do limite teórico (possível problema)")

    # Salvar resultado
    print("\n💾 Salvando resultado...")
    with open("output/bellmore_nemhauser.txt", "w", encoding="utf-8") as f:
        f.write(visualizar_bellmore_nemhauser(resultado, df))

    print("✅ Resultado salvo em output/bellmore_nemhauser.txt")
