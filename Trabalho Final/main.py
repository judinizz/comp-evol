import pandas as pd
import os
import pickle
from datetime import datetime, timedelta
from utils.tabu_search import tabu_search
from utils.avalia_rota import avaliar_rota


data_inicio_str = input("Data inicial (YYYY-MM-DD): ")
data_fim_str = input("Data final (YYYY-MM-DD): ")
hora_inicio_str = input("Horário de início (HH:MM): ")
hora_fim_str = input("Horário de término (HH:MM): ")
nome_bar_inicial = input("Nome do bar inicial (ou deixe em branco para escolha automática): ").strip()

data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
hora_fim = datetime.strptime(hora_fim_str, "%H:%M").time()

df = pd.read_csv("data/bares.csv")

with open("data/distancias.pkl", "rb") as f:
    distancias, tempos = pickle.load(f)

tempo_visita = timedelta(hours=1)
alpha, beta = 1.0, 25.0  #VARIAR


bar_inicial_idx = None
if nome_bar_inicial:
    # Busca o bar pelo nome (case-insensitive e busca parcial)
    mask = df['Nome do Buteco'].str.contains(nome_bar_inicial, case=False, na=False)
    bares_encontrados = df[mask]
    
    if len(bares_encontrados) == 0:
        print(f"Bar '{nome_bar_inicial}' não encontrado. Usando escolha automática.")
    elif len(bares_encontrados) == 1:
        bar_inicial_idx = bares_encontrados.index[0]
        print(f"Bar inicial escolhido: {bares_encontrados.iloc[0]['Nome do Buteco']}")
    else:
        print("Múltiplos bares encontrados:")
        for idx, bar in bares_encontrados.iterrows():
            print(f"- {bar['Nome do Buteco']}")
        print("Usando o primeiro encontrado.")
        bar_inicial_idx = bares_encontrados.index[0]
        print(f"Bar inicial escolhido: {bares_encontrados.iloc[0]['Nome do Buteco']}")


if bar_inicial_idx is not None:
    rota_inicial = [bar_inicial_idx] + [i for i in range(len(df)) if i != bar_inicial_idx]
else:
    rota_inicial = list(range(len(df)))
    print("Usando escolha automática para o bar inicial.")

#periodo total
hora_inicio_geral = datetime.combine(data_inicio, hora_inicio)
hora_fim_geral = datetime.combine(data_fim, hora_fim)

print(f"\nOtimizando rota do período completo:")
print(f"De: {hora_inicio_geral.strftime('%d/%m/%Y %H:%M')}")
print(f"Até: {hora_fim_geral.strftime('%d/%m/%Y %H:%M')}")


melhor_rota, custo = tabu_search(
    rota_inicial, tempos, df, hora_inicio_geral, hora_fim_geral, tempo_visita,
    alpha=alpha, beta=beta, tabu_tam=15, max_iter=20
)

print(f"\n=== ROTEIRO OTIMIZADO ===")
print(f"Custo total: {custo:.2f}")
print(f"Total de bares na rota: {len(melhor_rota)}")

hora_atual = hora_inicio_geral
dia_atual = data_inicio

print(f"\n--- Dia {dia_atual.strftime('%d/%m/%Y')} ---")
for i in range(len(melhor_rota)):
    bar = df.iloc[melhor_rota[i]]
    nome_bar = bar['Nome do Buteco']
    
    #mudança de dias
    if hora_atual.date() > dia_atual:
        dia_atual = hora_atual.date()
        print(f"\n--- Dia {dia_atual.strftime('%d/%m/%Y')} ---")
    

    horario_dia_inicio = datetime.combine(hora_atual.date(), hora_inicio)
    horario_dia_fim = datetime.combine(hora_atual.date(), hora_fim)
    
    if hora_atual < horario_dia_inicio:
        print(f"   (Aguardando abertura até {horario_dia_inicio.strftime('%H:%M')})")
        hora_atual = horario_dia_inicio
    
    if hora_atual > horario_dia_fim:
        proxima_data = hora_atual.date() + timedelta(days=1)
        if proxima_data <= data_fim:
            hora_atual = datetime.combine(proxima_data, hora_inicio)
            dia_atual = proxima_data
            print(f"\n--- Dia {dia_atual.strftime('%d/%m/%Y')} ---")
        else:
            print("Fim do período de viagem")
            break
    
    print(f"{i+1}. {nome_bar} - chegada: {hora_atual.strftime('%H:%M')}")
    

    if i < len(melhor_rota)-1:
        prox = melhor_rota[i+1]
        tempo_viagem = timedelta(minutes=tempos[melhor_rota[i]][prox])
        hora_atual += tempo_visita + tempo_viagem
    
    if hora_atual.time() > hora_fim:
        if hora_atual.date() < data_fim:
            print(f"   (Fim do horário do dia. Próxima visita no dia seguinte)")
        else:
            print("   (Fim do período de viagem)")
            break
