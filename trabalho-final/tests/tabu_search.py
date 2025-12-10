"""
Tabu Search Melhorado para TSP

Melhorias implementadas:
1. Operador 2-opt correto (inversão de segmento)
2. Lista tabu eficiente (armazena movimentos, não rotas)
3. Solução inicial pelo vizinho mais próximo
4. Mais iterações e melhor exploração
5. Critério de aspiração
"""

import random
from copy import deepcopy


def construir_solucao_vizinho_mais_proximo(distancias, inicio=0):
    """
    Constrói solução inicial usando heurística do vizinho mais próximo

    Args:
        distancias: Matriz de distâncias
        inicio: Vértice inicial

    Returns:
        Lista com a rota construída
    """
    n = len(distancias)
    nao_visitados = set(range(n))
    rota = [inicio]
    nao_visitados.remove(inicio)

    atual = inicio
    while nao_visitados:
        # Encontrar vizinho mais próximo
        menor_dist = float("inf")
        proximo = None

        for v in nao_visitados:
            dist = distancias[atual][v]
            if dist < menor_dist:
                menor_dist = dist
                proximo = v

        rota.append(proximo)
        nao_visitados.remove(proximo)
        atual = proximo

    return rota


def gerar_vizinhos_2opt(rota):
    """
    Gera vizinhos usando 2-opt CORRETO (inversão de segmento)

    Para cada par (i, j), inverte o segmento entre i e j:
    ... A - B - C - D - E - F ...
           i           j
    ... A - E - D - C - B - F ...

    Args:
        rota: Rota atual

    Returns:
        Lista de tuplas (nova_rota, i, j) onde i,j é o movimento
    """
    vizinhos = []
    n = len(rota)

    for i in range(n - 1):
        for j in range(i + 2, n):
            # Criar nova rota com segmento [i+1, j] invertido
            nova_rota = rota[: i + 1] + rota[i + 1 : j + 1][::-1] + rota[j + 1 :]
            vizinhos.append((nova_rota, i, j))

    return vizinhos


def avaliar_movimento_parcial(rota, i, j, distancias):
    """
    Avalia o impacto de um movimento 2-opt de forma incremental
    (mais eficiente que recalcular toda a rota)

    Args:
        rota: Rota atual
        i, j: Índices do movimento 2-opt
        distancias: Matriz de distâncias

    Returns:
        Diferença no custo (negativo = melhoria)
    """
    n = len(rota)

    # Arestas removidas
    custo_removido = 0
    if i > 0:
        custo_removido += distancias[rota[i]][rota[i + 1]]
    if j < n - 1:
        custo_removido += distancias[rota[j]][rota[j + 1]]

    # Arestas adicionadas
    custo_adicionado = 0
    if i > 0:
        custo_adicionado += distancias[rota[i]][rota[j]]
    if j < n - 1:
        custo_adicionado += distancias[rota[i + 1]][rota[j + 1]]

    return custo_adicionado - custo_removido


def tabu_search_melhorado(
    rota_inicial,
    distancias,
    tabu_tam=20,
    max_iter=200,
    max_iter_sem_melhoria=50,
    usar_solucao_inicial_inteligente=True,
    verbose=True,
):
    """
    Tabu Search melhorado para TSP

    Melhorias:
    - 2-opt correto
    - Lista tabu de movimentos
    - Critério de aspiração
    - Solução inicial pelo vizinho mais próximo
    - Mais iterações

    Args:
        rota_inicial: Rota inicial
        distancias: Matriz de distâncias
        tabu_tam: Tamanho da lista tabu
        max_iter: Máximo de iterações
        max_iter_sem_melhoria: Para se não melhorar após N iterações
        usar_solucao_inicial_inteligente: Se True, usa vizinho mais próximo
        verbose: Se True, imprime progresso

    Returns:
        Tupla (melhor_rota, melhor_distancia)
    """

    def avaliar_rota_simples(rota, distancias):
        """
        Avalia uma rota considerando apenas a distância total percorrida

        Args:
            rota: Lista com índices dos bares na ordem de visita
            distancias: Matriz de distâncias entre bares

        Returns:
            float: Distância total percorrida (incluindo retorno ao início)
        """
        if len(rota) < 2:
            return 0.0

        distancia_total = 0.0

        # Calcular distância entre bares consecutivos
        for i in range(len(rota) - 1):
            origem = rota[i]
            destino = rota[i + 1]
            distancia_total += distancias[origem][destino]

        # Adicionar distância de retorno ao ponto inicial (fechar o ciclo)
        distancia_total += distancias[rota[-1]][rota[0]]

        return distancia_total

    # Solução inicial
    if usar_solucao_inicial_inteligente:
        # Tentar várias soluções de vizinho mais próximo
        melhor_inicial = None
        melhor_dist_inicial = float("inf")

        # Testar 5 pontos de partida diferentes
        pontos_partida = random.sample(range(len(distancias)), min(5, len(distancias)))
        for inicio in pontos_partida:
            rota_teste = construir_solucao_vizinho_mais_proximo(distancias, inicio)
            dist_teste = avaliar_rota_simples(rota_teste, distancias)
            if dist_teste < melhor_dist_inicial:
                melhor_inicial = rota_teste
                melhor_dist_inicial = dist_teste

        atual = melhor_inicial
        if verbose:
            print(f"Solução inicial (vizinho mais próximo): {melhor_dist_inicial:.2f}")
    else:
        atual = deepcopy(rota_inicial)
        melhor_dist_inicial = avaliar_rota_simples(atual, distancias)
        if verbose:
            print(f"Solução inicial: {melhor_dist_inicial:.2f}")

    melhor = deepcopy(atual)
    melhor_distancia = avaliar_rota_simples(melhor, distancias)

    # Lista tabu armazena movimentos (i, j), não rotas completas
    tabu_movimentos = []

    # Histórico para gráficos
    historico = {"iteracao": [], "distancia_atual": [], "distancia_melhor": []}

    iteracoes_sem_melhoria = 0

    # Calcular distância atual para avaliação incremental
    distancia_atual = avaliar_rota_simples(atual, distancias)

    for iteracao in range(max_iter):
        vizinhos = gerar_vizinhos_2opt(atual)

        melhor_vizinho = None
        melhor_dist_vizinho = float("inf")
        melhor_movimento = None

        for nova_rota, i, j in vizinhos:
            movimento = (i, j)

            # AVALIAÇÃO INCREMENTAL: calcula apenas a diferença do movimento
            delta = avaliar_movimento_parcial(atual, i, j, distancias)
            dist = distancia_atual + delta

            # Critério de aspiração: aceita movimento tabu se melhora a melhor solução global
            movimento_tabu = movimento in tabu_movimentos
            criterio_aspiracao = dist < melhor_distancia

            if not movimento_tabu or criterio_aspiracao:
                if dist < melhor_dist_vizinho:
                    melhor_vizinho = nova_rota
                    melhor_dist_vizinho = dist
                    melhor_movimento = movimento

        if melhor_vizinho is None:
            if verbose:
                print(f"Iteração {iteracao}: Sem vizinhos válidos. Parando.")
            break

        # Atualizar solução atual
        atual = melhor_vizinho
        distancia_atual = (
            melhor_dist_vizinho  # Atualizar distância para próxima iteração
        )

        # Registrar histórico
        historico["iteracao"].append(iteracao)
        historico["distancia_atual"].append(melhor_dist_vizinho)
        historico["distancia_melhor"].append(melhor_distancia)

        # Atualizar melhor solução global
        if melhor_dist_vizinho < melhor_distancia:
            melhor = deepcopy(atual)
            melhor_distancia = melhor_dist_vizinho
            iteracoes_sem_melhoria = 0
            if verbose:
                melhoria = (
                    (melhor_dist_inicial - melhor_distancia) / melhor_dist_inicial * 100
                )
                print(
                    f"Iteração {iteracao}: Nova melhor = {melhor_distancia:.2f} (melhoria {melhoria:.1f}%)"
                )
        else:
            iteracoes_sem_melhoria += 1

        # Atualizar lista tabu
        if melhor_movimento:
            tabu_movimentos.append(melhor_movimento)
            if len(tabu_movimentos) > tabu_tam:
                tabu_movimentos.pop(0)

        # Critério de parada: sem melhoria por muito tempo
        if iteracoes_sem_melhoria >= max_iter_sem_melhoria:
            if verbose:
                print(
                    f"Iteração {iteracao}: Sem melhoria por {max_iter_sem_melhoria} iterações. Parando."
                )
            break

    if verbose:
        melhoria_final = (
            (melhor_dist_inicial - melhor_distancia) / melhor_dist_inicial * 100
        )
        print("\n✅ Tabu Search concluído!")
        print(f"   Distância inicial: {melhor_dist_inicial:.2f}")
        print(f"   Distância final: {melhor_distancia:.2f}")
        print(f"   Melhoria: {melhoria_final:.1f}%")
        print(f"   Iterações executadas: {iteracao + 1}")

    return melhor, melhor_distancia, historico


def tabu_search_melhorado_com_penalidades(
    rota_inicial,
    tempos,
    bares,
    hora_inicial,
    hora_final,
    tempo_visita,
    distancias=None,
    alpha=1.0,
    beta=20.0,
    tabu_tam=10,
    max_iter=100,
    max_iter_sem_melhoria=30,
    usar_solucao_inicial_inteligente=True,
    verbose=True,
):
    """
    Tabu Search MELHORADO para problema COMPLETO com penalidades

    Aplica as mesmas melhorias do tabu_search_melhorado (TSP simples):
    - 2-opt correto
    - Lista tabu de movimentos
    - Solução inicial inteligente
    - Critério de aspiração
    - Parâmetros otimizados da Config 1

    Mas usa avaliar_rota (com penalidades de horários, notas, etc.)

    Args:
        rota_inicial: Rota inicial
        tempos: Matriz de tempos
        bares: DataFrame com informações dos bares
        hora_inicial: Hora de início
        hora_final: Hora limite
        tempo_visita: Tempo de visita por bar
        distancias: Matriz de distâncias (para solução inicial)
        alpha: Peso do tempo
        beta: Peso das notas
        tabu_tam: Tamanho da lista tabu (Config 1: 10)
        max_iter: Máximo de iterações (Config 1: 100)
        max_iter_sem_melhoria: Para após N iterações (Config 1: 30)
        usar_solucao_inicial_inteligente: Se True, usa vizinho mais próximo
        verbose: Se True, imprime progresso

    Returns:
        Tupla (melhor_rota, melhor_custo)
    """
    try:
        from utils.avalia_rota import avaliar_rota
    except ImportError:
        from avalia_rota import avaliar_rota

    # Solução inicial inteligente
    if usar_solucao_inicial_inteligente and distancias is not None:
        if verbose:
            print("🔨 Construindo solução inicial inteligente...")

        melhor_inicial = None
        melhor_custo_inicial = float("inf")

        # Testar 3 pontos de partida diferentes
        pontos_partida = random.sample(range(len(bares)), min(3, len(bares)))
        for inicio in pontos_partida:
            rota_teste = construir_solucao_vizinho_mais_proximo(distancias, inicio)
            custo_teste = avaliar_rota(
                rota_teste,
                tempos,
                bares,
                hora_inicial,
                hora_final,
                tempo_visita,
                alpha,
                beta,
            )

            if custo_teste < melhor_custo_inicial:
                melhor_inicial = rota_teste
                melhor_custo_inicial = custo_teste

        atual = melhor_inicial
        if verbose:
            print(f"   Custo inicial: {melhor_custo_inicial:.2f}")
    else:
        atual = deepcopy(rota_inicial)
        melhor_custo_inicial = avaliar_rota(
            atual, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta
        )
        if verbose:
            print(f"Custo inicial: {melhor_custo_inicial:.2f}")

    melhor = deepcopy(atual)
    melhor_custo = avaliar_rota(
        melhor, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta
    )

    # Lista tabu armazena MOVIMENTOS (i, j), não rotas completas
    tabu_movimentos = []

    iteracoes_sem_melhoria = 0

    if verbose:
        print("\n🔍 Iniciando busca tabu...")
        print(f"   Parâmetros: tabu_tam={tabu_tam}, max_iter={max_iter}")
        print(f"   Alpha={alpha:.2f}, Beta={beta:.2f}")

    for iteracao in range(max_iter):
        # Gerar vizinhos com operador 2-opt CORRETO
        vizinhos = gerar_vizinhos_2opt(atual)

        melhor_vizinho = None
        melhor_custo_vizinho = float("inf")
        melhor_movimento = None

        for nova_rota, i, j in vizinhos:
            movimento = (i, j)
            custo = avaliar_rota(
                nova_rota,
                tempos,
                bares,
                hora_inicial,
                hora_final,
                tempo_visita,
                alpha,
                beta,
            )

            # Critério de aspiração: aceita movimento tabu se melhora melhor solução global
            movimento_tabu = movimento in tabu_movimentos
            criterio_aspiracao = custo < melhor_custo

            if not movimento_tabu or criterio_aspiracao:
                if custo < melhor_custo_vizinho:
                    melhor_vizinho = nova_rota
                    melhor_custo_vizinho = custo
                    melhor_movimento = movimento

        if melhor_vizinho is None:
            if verbose:
                print(f"   Iteração {iteracao}: Sem vizinhos válidos. Parando.")
            break

        # Atualizar solução atual
        atual = melhor_vizinho

        # Atualizar melhor solução global
        if melhor_custo_vizinho < melhor_custo:
            melhor = deepcopy(atual)
            melhor_custo = melhor_custo_vizinho
            iteracoes_sem_melhoria = 0

            if verbose and (iteracao < 10 or iteracao % 10 == 0):
                melhoria = (
                    (melhor_custo_inicial - melhor_custo)
                    / abs(melhor_custo_inicial)
                    * 100
                )
                print(
                    f"   Iteração {iteracao}: Custo = {melhor_custo:.2f} (melhoria {melhoria:.1f}%)"
                )
        else:
            iteracoes_sem_melhoria += 1

        # Atualizar lista tabu de movimentos
        if melhor_movimento:
            tabu_movimentos.append(melhor_movimento)
            if len(tabu_movimentos) > tabu_tam:
                tabu_movimentos.pop(0)

        # Parada inteligente: sem melhoria por muito tempo
        if iteracoes_sem_melhoria >= max_iter_sem_melhoria:
            if verbose:
                print(
                    f"   Iteração {iteracao}: Sem melhoria por {max_iter_sem_melhoria} iterações. Parando."
                )
            break

    if verbose:
        melhoria_final = (
            (melhor_custo_inicial - melhor_custo) / abs(melhor_custo_inicial) * 100
        )
        print("\n✅ Busca concluída!")
        print(f"   Custo inicial: {melhor_custo_inicial:.2f}")
        print(f"   Custo final: {melhor_custo:.2f}")
        print(f"   Melhoria: {melhoria_final:.1f}%")
        print(f"   Iterações: {iteracao + 1}")

    return melhor, melhor_custo


if __name__ == "__main__":
    """Teste do Tabu Search melhorado"""
    import pickle
    from datetime import datetime, timedelta

    import pandas as pd

    print("=" * 80)
    print("TESTES: Tabu Search Melhorado")
    print("=" * 80)

    print("\n🔄 Carregando dados...")
    df = pd.read_csv("data/bares.csv")

    with open("data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)

    print(f"✅ {len(df)} bares carregados\n")

    # ========== TESTE 1: TSP Simples (sem penalidades) ==========
    print("\n" + "=" * 80)
    print("TESTE 1: TSP Simples (otimização de distância)")
    print("=" * 80)

    rota_inicial = list(range(len(df)))

    melhor_rota, melhor_dist, historico = tabu_search_melhorado(
        rota_inicial,
        distancias,
        tabu_tam=10,
        max_iter=100,
        max_iter_sem_melhoria=30,
        usar_solucao_inicial_inteligente=True,
        verbose=True,
    )

    print(f"\n🎯 Resultado final: {melhor_dist:.2f} km")

    # ========== TESTE 2: Problema Completo (com penalidades) ==========
    print("\n\n" + "=" * 80)
    print("TESTE 2: Problema Completo (com horários e penalidades)")
    print("=" * 80)

    n_bares = min(15, len(df))
    rota_inicial_complexo = list(range(n_bares))

    hora_inicial = datetime(2024, 11, 12, 18, 0)
    hora_final = datetime(2024, 11, 12, 23, 0)
    tempo_visita = timedelta(minutes=30)

    print(f"Número de bares: {n_bares}")
    print(
        f"Horário: {hora_inicial.strftime('%H:%M')} às {hora_final.strftime('%H:%M')}"
    )
    print(f"Tempo de visita: {tempo_visita.seconds // 60} minutos\n")

    melhor_rota_complexo, melhor_custo_complexo = tabu_search_melhorado_com_penalidades(
        rota_inicial=rota_inicial_complexo,
        tempos=tempos,
        bares=df,
        hora_inicial=hora_inicial,
        hora_final=hora_final,
        tempo_visita=tempo_visita,
        distancias=distancias,
        alpha=1.0,
        beta=20.0,
        tabu_tam=10,
        max_iter=100,
        max_iter_sem_melhoria=30,
        usar_solucao_inicial_inteligente=True,
        verbose=True,
    )

    print(f"\n🎯 Resultado final: {melhor_custo_complexo:.2f}")
    print("\nPrimeiros 10 bares da sequência:")
    for i, idx_bar in enumerate(melhor_rota_complexo[:10]):
        nome_bar = df.iloc[idx_bar]["Nome do Buteco"]
        print(f"   {i + 1}. {nome_bar}")

    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES CONCLUÍDOS")
    print("=" * 80)
