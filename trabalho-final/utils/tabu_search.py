import random
from copy import deepcopy

try:
    from .avalia_rota import avaliar_rota
except Exception:
    from avalia_rota import avaliar_rota


def construir_solucao_vizinho_mais_proximo(distancias, inicio=0):
    n = len(distancias)
    nao_visitados = set(range(n))
    rota = [inicio]
    nao_visitados.remove(inicio)

    atual = inicio
    while nao_visitados:
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
    vizinhos = []
    n = len(rota)
    for i in range(n - 1):
        for j in range(i + 2, n):
            nova_rota = rota[: i + 1] + rota[i + 1 : j + 1][::-1] + rota[j + 1 :]
            vizinhos.append((nova_rota, i, j))
    return vizinhos


def avaliar_movimento_parcial(rota, i, j, distancias):
    n = len(rota)
    custo_removido = 0
    if i >= 0:
        custo_removido += distancias[rota[i]][rota[i + 1]]
    if j < n - 1:
        custo_removido += distancias[rota[j]][rota[j + 1]]

    custo_adicionado = 0
    if i >= 0:
        custo_adicionado += distancias[rota[i]][rota[j]]
    if j < n - 1:
        custo_adicionado += distancias[rota[i + 1]][rota[j + 1]]

    return custo_adicionado - custo_removido


def tabu_search(
    rota_inicial,
    tempos,
    bares,
    hora_inicial,
    hora_final,
    tempo_visita,
    alpha=1.0,
    beta=20.0,
    tabu_tam=10,
    max_iter=100,
    max_iter_sem_melhoria=30,
    usar_solucao_inicial_inteligente=True,
    verbose=True,
):
    """Melhorada: 2-opt correto, lista tabu de movimentos, solução inicial NN, avaliação incremental."""

    # Se solicitado, construir solução inicial inteligente
    if usar_solucao_inicial_inteligente:
        melhor_inicial = None
        melhor_dist_inicial = float("inf")
        pontos = random.sample(range(len(bares)), min(3, len(bares)))
        for inicio in pontos:
            rota_teste = construir_solucao_vizinho_mais_proximo(tempos, inicio)
            dist_teste = avaliar_rota(
                rota_teste,
                tempos,
                bares,
                hora_inicial,
                hora_final,
                tempo_visita,
                alpha,
                beta,
            )
            if dist_teste < melhor_dist_inicial:
                melhor_inicial = rota_teste
                melhor_dist_inicial = dist_teste

        # Fallback: se nenhuma rota NN foi válida, usar rota_inicial
        if melhor_inicial is None:
            melhor_inicial = rota_inicial
            melhor_dist_inicial = avaliar_rota(
                melhor_inicial,
                tempos,
                bares,
                hora_inicial,
                hora_final,
                tempo_visita,
                alpha,
                beta,
            )
            if verbose:
                print(
                    f"Solução inicial (fallback para rota_inicial): {melhor_dist_inicial:.2f}"
                )
        else:
            if verbose:
                print(f"Solução inicial (NN): {melhor_dist_inicial:.2f}")

        atual = deepcopy(melhor_inicial)
    else:
        atual = deepcopy(rota_inicial)
        melhor_dist_inicial = avaliar_rota(
            atual, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta
        )
        if verbose:
            print(f"Solução inicial: {melhor_dist_inicial:.2f}")

    melhor = deepcopy(atual)
    melhor_custo = avaliar_rota(
        melhor, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta
    )

    tabu_movimentos = []
    historico = {"iteracao": [], "distancia_atual": [], "distancia_melhor": []}
    iteracoes_sem_melhoria = 0

    distancia_atual = avaliar_rota(
        atual, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha, beta
    )

    for iteracao in range(max_iter):
        vizinhos = gerar_vizinhos_2opt(atual)
        melhor_vizinho = None
        melhor_dist_vizinho = float("inf")
        melhor_movimento = None

        for nova_rota, i, j in vizinhos:
            movimento = (i, j)
            delta = avaliar_movimento_parcial(atual, i, j, tempos)
            dist = distancia_atual + delta
            movimento_tabu = movimento in tabu_movimentos
            criterio_aspiracao = dist < melhor_custo
            if not movimento_tabu or criterio_aspiracao:
                if dist < melhor_dist_vizinho:
                    melhor_vizinho = nova_rota
                    melhor_dist_vizinho = dist
                    melhor_movimento = movimento

        if melhor_vizinho is None:
            if verbose:
                print(f"Iteração {iteracao}: Sem vizinhos válidos. Parando.")
            break

        atual = melhor_vizinho
        distancia_atual = melhor_dist_vizinho

        historico["iteracao"].append(iteracao)
        historico["distancia_atual"].append(melhor_dist_vizinho)
        historico["distancia_melhor"].append(melhor_custo)

        if melhor_dist_vizinho < melhor_custo:
            melhor = deepcopy(atual)
            melhor_custo = melhor_dist_vizinho
            iteracoes_sem_melhoria = 0
            if verbose:
                melhoria = (
                    (melhor_dist_inicial - melhor_custo) / melhor_dist_inicial * 100
                )
                print(
                    f"Iteração {iteracao}: Nova melhor = {melhor_custo:.2f} (melhoria {melhoria:.1f}%)"
                )
        else:
            iteracoes_sem_melhoria += 1

        if melhor_movimento:
            tabu_movimentos.append(melhor_movimento)
            if len(tabu_movimentos) > tabu_tam:
                tabu_movimentos.pop(0)

        if iteracoes_sem_melhoria >= max_iter_sem_melhoria:
            if verbose:
                print(
                    f"Iteração {iteracao}: Sem melhoria por {max_iter_sem_melhoria} iterações. Parando."
                )
            break

    if verbose:
        melhoria_final = (
            (melhor_dist_inicial - melhor_custo) / melhor_dist_inicial * 100
            if melhor_dist_inicial
            else 0
        )
        print("\n✅ Tabu Search concluído!")
        print(f"   Distância inicial: {melhor_dist_inicial:.2f}")
        print(f"   Distância final: {melhor_custo:.2f}")
        print(f"   Melhoria: {melhoria_final:.1f}%")

    return melhor, melhor_custo, historico


if __name__ == "__main__":
    import pickle
    from datetime import datetime, timedelta

    import pandas as pd

    print("TESTES: Tabu Search Melhorado")
    df = pd.read_csv("../data/bares.csv")
    with open("../data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)

    rota_inicial = list(range(min(10, len(df))))

    melhor_rota, melhor_dist, historico = tabu_search(
        rota_inicial,
        tempos,
        df,
        datetime(2024, 11, 12, 18, 0),
        datetime(2024, 11, 12, 23, 0),
        timedelta(minutes=30),
        tabu_tam=10,
        max_iter=50,
        usar_solucao_inicial_inteligente=True,
        verbose=True,
    )

    print(f"\nResultado final: {melhor_dist:.2f} km")