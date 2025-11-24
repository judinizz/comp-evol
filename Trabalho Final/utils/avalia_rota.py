import pandas as pd
from datetime import datetime, timedelta

DIAS_SEMANA = {
    0: "Seg",      
    1: "Ter",      
    2: "Qua",     
    3: "Qui",      
    4: "Sex",     
    5: "Sáb",     
    6: "Dom"       
}

def avaliar_rota(rota, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha=1.0, beta=20.0):
    """
    Avalia uma rota considerando múltiplos dias e horários de funcionamento
    """
    hora_atual = hora_inicial
    tempo_total = 0
    soma_notas = 0
    penalidade = 0
    
    # Extrai horários diários do período
    data_inicio = hora_inicial.date()
    data_fim = hora_final.date()
    hora_dia_inicio = hora_inicial.time()
    hora_dia_fim = hora_final.time()

    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]
        bar_dest = bares.iloc[destino]

        # Calcula tempo de deslocamento
        tempo_desloc = timedelta(minutes=tempos[origem][destino])
        nova_hora = hora_atual + tempo_desloc
        tempo_total += tempos[origem][destino]

        # Verifica se ultrapassou o horário do dia atual
        hora_limite_dia = datetime.combine(nova_hora.date(), hora_dia_fim)
        
        if nova_hora > hora_limite_dia and nova_hora.date() <= data_fim:
            # Pula para o próximo dia
            proxima_data = nova_hora.date() + timedelta(days=1)
            if proxima_data <= data_fim:
                nova_hora = datetime.combine(proxima_data, hora_dia_inicio)
                penalidade += 100  # pequena penalidade por pular de dia
            else:
                # Ultrapassou o período total
                penalidade += 5000
                break
        elif nova_hora > hora_final:
            # Ultrapassou o período total
            penalidade += 5000
            break

        hora_atual = nova_hora

        # Verifica horário de funcionamento do bar
        dia_semana = DIAS_SEMANA[hora_atual.weekday()]
        abertura_col = f"{dia_semana} (Abertura)"
        fechamento_col = f"{dia_semana} (Fechamento)"

        if abertura_col not in bares.columns or fechamento_col not in bares.columns:
            penalidade += 1000
            continue

        abertura_str = bar_dest[abertura_col]
        fechamento_str = bar_dest[fechamento_col]
        
        # Se não tem horário, considera que não abre neste dia
        if pd.isna(abertura_str) or pd.isna(fechamento_str) or abertura_str == "" or fechamento_str == "":
            penalidade += 1000
            continue

        try:
            # Parse dos horários de funcionamento
            if ':' in str(abertura_str):
                if len(str(abertura_str).split(':')) == 3:
                    abertura = datetime.combine(hora_atual.date(), datetime.strptime(str(abertura_str), "%H:%M:%S").time())
                else:
                    abertura = datetime.combine(hora_atual.date(), datetime.strptime(str(abertura_str), "%H:%M").time())
            else:
                abertura = datetime.combine(hora_atual.date(), datetime.strptime(str(abertura_str), "%H:%M").time())
                
            if ':' in str(fechamento_str):
                if len(str(fechamento_str).split(':')) == 3:
                    fechamento = datetime.combine(hora_atual.date(), datetime.strptime(str(fechamento_str), "%H:%M:%S").time())
                else:
                    fechamento = datetime.combine(hora_atual.date(), datetime.strptime(str(fechamento_str), "%H:%M").time())
            else:
                fechamento = datetime.combine(hora_atual.date(), datetime.strptime(str(fechamento_str), "%H:%M").time())
                
        except ValueError:
            penalidade += 1000
            continue
            
        # Ajusta fechamento se for no dia seguinte
        if fechamento < abertura:
            fechamento += timedelta(days=1)

        # Verifica se está dentro do horário de funcionamento
        if not (abertura <= hora_atual <= fechamento):
            penalidade += 1000
        else:
            # Adiciona nota do bar (usando nota padrão)
            nota_bar = 5.0
            soma_notas += nota_bar

        # Adiciona tempo de visita
        hora_atual += tempo_visita

    custo = alpha * tempo_total - beta * soma_notas + penalidade
    return custo
