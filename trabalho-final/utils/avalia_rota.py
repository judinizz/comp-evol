from datetime import datetime, timedelta

import pandas as pd


class CacheHorarios:
    """Cache simples para horários de abertura/fechamento por bar e dia da semana.

    Armazena tuplas (abertura, fechamento) onde cada um é timedelta desde meia-noite
    ou None quando não informado.
    """

    DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    def __init__(self, bares_df: pd.DataFrame):
        self.bares_df = bares_df
        self._cache = {}

    @staticmethod
    def _parse_horario(valor):
        if valor is None:
            return None
        try:
            s = str(valor).strip()
            if s == "" or s.lower() in {"nan", "none"}:
                return None
            parts = s.split(":")
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return timedelta(hours=h, minutes=m)
        except Exception:
            return None

    def obter(self, idx_bar: int, dia_semana: int):
        chave = (idx_bar, dia_semana)
        if chave in self._cache:
            return self._cache[chave]

        row = self.bares_df.iloc[idx_bar] if idx_bar < len(self.bares_df) else None
        if row is None:
            self._cache[chave] = (None, None)
            return (None, None)

        col_ab = f"{self.DIAS[dia_semana]} (Abertura)"
        col_fc = f"{self.DIAS[dia_semana]} (Fechamento)"

        ab = self._parse_horario(row.get(col_ab, None))
        fc = self._parse_horario(row.get(col_fc, None))
        self._cache[chave] = (ab, fc)
        return (ab, fc)


def avaliar_rota(
    rota, tempos, bares, hora_inicial, hora_final, tempo_visita, alpha=1.0, beta=20.0
):
    """
    Avalia uma rota retornando um custo numérico menor = melhor.

    O custo combina:
     - tempo total de locomoção + visitas (em minutos)
     - penalidades por chegar fora do horário de funcionamento
     - recompensa por nota (beta * soma_notas)

    Otimizações implementadas:
     - CacheHorarios para evitar parsing repetido de strings das colunas
     - iteração linear sobre a rota
    """

    # normalizações e caches
    cache = CacheHorarios(bares)
    total_tempo = 0.0 
    total_nota = 0.0
    penalidade = 0.0

    hora_atual = hora_inicial

    n = len(rota)
    if n == 0:
        return float("inf")

    # itera sobre a sequência (não fechamos a rota em ciclo a menos que queira)
    for pos in range(n - 1):
        origem = rota[pos]
        destino = rota[pos + 1]

        t = float(tempos[origem][destino])
        total_tempo += t
        hora_atual = hora_atual + timedelta(minutes=t)

        visita_min = (
            tempo_visita.total_seconds() / 60.0
            if isinstance(tempo_visita, timedelta)
            else float(tempo_visita)
        )
        total_tempo += visita_min
        hora_atual = hora_atual + timedelta(minutes=visita_min)

        row = bares.iloc[destino]
        nota = 0.0
        if "Nota" in bares.columns:
            try:
                nota = float(row.get("Nota", 0) or 0)
            except Exception:
                nota = 0.0

        total_nota += nota

        # penalidades por horário (usando cache)
        dia = hora_atual.weekday()
        hor_ab, hor_fc = cache.obter(destino, dia)
        if hor_ab is not None and hor_fc is not None:
            desde_meia_noite = timedelta(
                hours=hora_atual.hour, minutes=hora_atual.minute
            )
            if desde_meia_noite < hor_ab:
                diff = (hor_ab - desde_meia_noite).total_seconds() / 60.0
                penalidade += diff * 2.0
            elif desde_meia_noite > hor_fc:
                penalidade += 1000.0

    # custo final: tempo ponderado + penalidades - recompensa por notas
    custo = alpha * total_tempo + penalidade - beta * total_nota
    return float(custo)


if __name__ == "__main__":
    import pickle
    from datetime import datetime, timedelta

    import pandas as pd

    df = pd.read_csv("../data/bares.csv")
    with open("../data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)

    rota = list(range(min(8, len(df))))
    custo = avaliar_rota(
        rota,
        tempos,
        df,
        datetime(2024, 11, 12, 18, 0),
        datetime(2024, 11, 12, 23, 0),
        timedelta(minutes=30),
    )
    print(f"Custo (teste): {custo}")