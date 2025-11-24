import pandas as pd
from datetime import time

def filtrar_bares(df, nota_min=0, preco_max=None, hora_inicio=None, hora_fim=None):
    filtrado = df.copy()

    if nota_min:
        filtrado = filtrado[filtrado["nota"] >= nota_min]

    if preco_max:
        filtrado = filtrado[filtrado["preco"] <= preco_max]

    if hora_inicio and hora_fim:
        def aberto_no_intervalo(row):
            h_abre = pd.to_datetime(row["abertura"], format="%H:%M").time()
            h_fecha = pd.to_datetime(row["fechamento"], format="%H:%M").time()
            return not (hora_fim < h_abre or hora_inicio > h_fecha)
        filtrado = filtrado[filtrado.apply(aberto_no_intervalo, axis=1)]

    return filtrado.reset_index(drop=True)


