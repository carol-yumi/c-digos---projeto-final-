"""
comum_parte4.py -- configuracao e leitores usados por todos os scripts da Parte 4.

De onde vem cada coisa (dados reais, tudo a partir da raiz do repositorio):
  Parte 1 (Parte1_construcao_painel_fundamentalista.py) -> resultados_parte1/painel_modelagem.parquet
                                                            resultados_parte1/dicionario_variaveis.csv
  Parte 2 (Parte2_treino.py --modo cv)                  -> resultados/run_<hash>/previsoes_oos.parquet
                                                            resultados/run_<hash>/blocos_AAAAMM.parquet
                                                            resultados/run_<hash>/modelos/modelo_AAAAMM_<alvo>_<k>.txt
                                                            resultados/run_<hash>/config.json
  Precos (Economatica)                                  -> Cotação.xlsx ou cotacao_diaria.csv
  Fatores (NEFIN + CDI)                                 -> fatores.parquet  (data, rf, mkt, smb, hml, wml, iml)
A Parte 4 escolhe sozinha a rodada mais recente da Parte 2 em modo cv e o painel cujo hash bate com o usado
nessa rodada. Para testar sem dados reais: rode simula_dados.py e ponha USAR_DADOS_SIMULADOS = True.

Requisitos da Parte 2 para SHAP e peer weights: rodar SEM --sem-modelos (os modelos precisam ser salvos) e
manter perda L2 sem regularizacao/bagging (ja e assim em PARAMS_PAPER e PARAMS_PEQUENA).
"""
import json
import os
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

# ------------------------------------------------------------------ configuracao principal
USAR_DADOS_SIMULADOS = False     # True = usa dados_sim/ (gerados por simula_dados.py)
RUN_PARTE2 = None                # ex.: "run_3f2a9c1b7d"; None = rodada mais recente da Parte 2 em modo cv
# janela de analise da Parte 4: meses de FORMACAO da carteira (o retorno e medido no mes seguinte).
# Combinado do grupo: out/2006 a out/2026. None = sem limite.
INICIO_ANALISE = "2006-10-31"
FIM_ANALISE = "2026-10-31"
if os.environ.get("PARTE4_SIMULADO") == "1":      # atalho para testes: PARTE4_SIMULADO=1 python ...
    USAR_DADOS_SIMULADOS = True

PASTA = Path(__file__).parent
PASTA_SIM = PASTA / "dados_sim"
BASE_DADOS = PASTA_SIM if USAR_DADOS_SIMULADOS else PASTA
PASTA_RESULTADOS_P2 = BASE_DADOS / "resultados"
PAINEIS_CANDIDATOS = [BASE_DADOS / "resultados_parte1" / "painel_modelagem.parquet", BASE_DADOS / "painel_modelagem.parquet"]
DICIONARIOS_CANDIDATOS = [BASE_DADOS / "resultados_parte1" / "dicionario_variaveis.csv", BASE_DADOS / "dicionario_variaveis.csv"]
COTACOES_CANDIDATAS = [BASE_DADOS / "Cotação.xlsx", BASE_DADOS / "cotacao_diaria.csv"]
ARQ_RETORNOS = BASE_DADOS / "retornos.parquet"       # gerado automaticamente a partir da cotacao
ARQ_FATORES = BASE_DADOS / "fatores.parquet"        # gerado automaticamente a partir do NEFIN
ARQ_LIQUIDEZ = BASE_DADOS / "liquidez.parquet"       # gerado automaticamente a partir da cotacao
ARQ_NEFIN_LOCAL = BASE_DADOS / "nefin_factors_monthly.csv"   # opcional: arquivo do NEFIN baixado a mao
URL_NEFIN = "https://nefin.com.br/nefindata/risk-factors/nefin_factors_monthly.csv"   # nefin.com.br/data/risk-factors/
PASTA_SAIDA = BASE_DADOS / "resultados_parte4"

ALVOS = ("lnm2b", "lnv2a", "lnv2s")
ALVOS_EV = ("lnv2a", "lnv2s")
DENOM = {"lnm2b": "pl", "lnv2a": "ativos", "lnv2s": "vendas"}
N_BLOCOS = 5
COL_EPSILON = "erro_pct_vm"      # "erro_pct_vm_smear" usa o fator de Duan da Parte 2 (sensibilidade)
COLS_PREV = ["ticker", "data", "alvo", "bloco", "log_real", "pred_log", "valor_mercado", COL_EPSILON]

# ------------------------------------------------------------------ parametros das carteiras (4.1)
N_QUANTIS = 5
BREAKPOINTS = "todas"        # "todas" | "grandes": cortes so com acoes acima da mediana de VM (analogo NYSE)
FILTRO_EW_PCTL_VM = 0.20     # carteiras EW excluem acoes abaixo deste percentil de VM do mes (paper: 0.20)
EXCLUI_VM_PREV_NAO_POSITIVO = False
LAGS_NEWEY_WEST = 6
FATORES_MODELO = {"CAPM": ["mkt"], "NEFIN5": ["mkt", "smb", "hml", "wml", "iml"]}
# filtro de liquidez: a acao so entra nas carteiras de t se negociou em pelo menos PRESENCA_MINIMA dos pregoes da
# janela [t - JANELA_LIQUIDEZ_MESES, t] (contados a partir da primeira cotacao, para nao excluir IPOs recentes)
# e se ha pelo menos MIN_PREGOES pregoes nessa janela. Usa so informacao ate t. None desliga o filtro.
PRESENCA_MINIMA = 0.80
JANELA_LIQUIDEZ_MESES = 12
MIN_PREGOES = 63              # ~3 meses de historico

# ------------------------------------------------------------------ parametros do SHAP (4.2)
PERIODOS = {"2007-2010": (2006, 2010), "2011-2015": (2011, 2015), "2016-2020": (2016, 2020), "2021-2026": (2021, 2026)}


def bloco_validacao(k):
    """Mesma regra do Parte2_treino.roda_mes_cv: validacao = bloco (k + 1) % 5."""
    return (k + 1) % N_BLOCOS


# ------------------------------------------------------------------ rodada da Parte 2
def pasta_run():
    if RUN_PARTE2:
        d = PASTA_RESULTADOS_P2 / RUN_PARTE2
        if not (d / "previsoes_oos.parquet").exists():
            raise FileNotFoundError(f"{d} nao tem previsoes_oos.parquet")
        return d
    runs = []
    for arq in PASTA_RESULTADOS_P2.glob("run_*/previsoes_oos.parquet"):
        cfg = arq.parent / "config.json"
        if cfg.exists() and json.loads(cfg.read_text(encoding="utf-8")).get("modo") == "cv":
            runs.append(arq.parent)
    if not runs:
        raise FileNotFoundError(
            f"Nenhuma rodada da Parte 2 em modo cv em {PASTA_RESULTADOS_P2}. Rode antes:\n"
            "    python Parte2_treino.py --modo cv --n-meses 0\n"
            "(sem --sem-modelos). Para testar com dados falsos: python simula_dados.py e "
            "USAR_DADOS_SIMULADOS = True em comum_parte4.py.")
    return max(runs, key=lambda d: (d / "previsoes_oos.parquet").stat().st_mtime)


def config_run():
    return json.loads((pasta_run() / "config.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ leitores
def ler_previsoes():
    run = pasta_run()
    p = pd.read_parquet(run / "previsoes_oos.parquet")
    falt = [c for c in COLS_PREV if c not in p.columns]
    if falt:
        raise KeyError(f"{run.name}/previsoes_oos.parquet sem as colunas {falt}")
    p["data"] = pd.to_datetime(p["data"]) + pd.offsets.MonthEnd(0)
    p = p[p["bloco"] >= 0]
    if INICIO_ANALISE:
        p = p[p["data"] >= pd.Timestamp(INICIO_ANALISE)]
    if FIM_ANALISE:
        p = p[p["data"] <= pd.Timestamp(FIM_ANALISE)]
    dup = int(p.duplicated(["ticker", "data", "alvo"]).sum())
    if dup:
        raise ValueError(f"{dup} previsoes duplicadas em (ticker, data, alvo)")
    print(f"previsoes: {run.name} | {len(p)} linhas | {p['data'].min():%Y-%m} a {p['data'].max():%Y-%m}")
    return p


def _sha256(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def arquivo_painel():
    """O painel usado no treino da rodada (confere o hash gravado no config.json da Parte 2)."""
    existentes = [p for p in PAINEIS_CANDIDATOS if p.exists()]
    if not existentes:
        raise FileNotFoundError(f"painel_modelagem.parquet nao encontrado em {[str(p) for p in PAINEIS_CANDIDATOS]}")
    try:
        alvo_hash = config_run().get("sha256_painel")
    except FileNotFoundError:
        alvo_hash = None
    if alvo_hash:
        for p in existentes:
            if _sha256(p) == alvo_hash:
                return p
        warnings.warn("nenhum painel tem o mesmo hash do usado na Parte 2: SHAP e peer weights vao acusar "
                      "diferenca se o painel mudou depois do treino")
    return existentes[0]


def ler_painel(colunas=None):
    arq = arquivo_painel()
    p = pd.read_parquet(arq, columns=colunas)
    p["data"] = pd.to_datetime(p["data"]) + pd.offsets.MonthEnd(0)
    return p


def ler_dicionario():
    for arq in DICIONARIOS_CANDIDATOS:
        if arq.exists():
            d = pd.read_csv(arq, encoding="utf-8-sig")
            if {"nome", "categoria"} <= set(d.columns):
                return d
    warnings.warn("dicionario_variaveis.csv nao encontrado: todas as variaveis ficam 'Sem categoria'")
    return pd.DataFrame(columns=["nome", "categoria"])


def caminho_modelo(alvo, data, bloco):
    return pasta_run() / "modelos" / f"modelo_{pd.Timestamp(data):%Y%m}_{alvo}_{int(bloco)}.txt"


def carrega_modelo(alvo, data, bloco):
    arq = caminho_modelo(alvo, data, bloco)
    if not arq.exists():
        raise FileNotFoundError(f"modelo ausente: {arq}. A Parte 2 foi rodada com --sem-modelos?")
    return lgb.Booster(model_file=str(arq))


def taxa_aprendizado(booster, padrao=0.1):
    for linha in booster.model_to_string().splitlines():
        if linha.startswith("[learning_rate:"):
            return float(linha.split(":")[1].strip(" ]"))
    return padrao


def parametros_gravados(booster):
    out = {}
    for linha in booster.model_to_string().splitlines():
        if linha.startswith("[") and ":" in linha:
            k, v = linha.strip("[]").split(":", 1)
            out[k.strip()] = v.strip()
    return out


def matriz_features(painel_mes, booster):
    """X na ordem de features do modelo, com as categorias (setor/industry) codificadas como no treino."""
    nomes = booster.feature_name()
    falt = [c for c in nomes if c not in painel_mes.columns]
    if falt:
        raise KeyError(f"features do modelo ausentes no painel: {falt}")
    X = painel_mes[nomes].copy()
    cats = getattr(booster, "pandas_categorical", None) or []
    cat_cols = [c for c in nomes if isinstance(X[c].dtype, pd.CategoricalDtype) or X[c].dtype == object
                or pd.api.types.is_string_dtype(X[c])]
    for c, niveis in zip(cat_cols, cats):
        X[c] = pd.Categorical(X[c].astype(object), categories=niveis)
    return X


def filtra_alvo(df, alvo):
    """Mesmo filtro do Parte2_treino.filtra_alvo."""
    ok = np.isfinite(df[alvo].to_numpy(dtype=float))
    ok &= df[DENOM[alvo]].to_numpy(dtype=float) > 0
    ok &= df["valor_mercado"].to_numpy(dtype=float) > 0
    if alvo in ALVOS_EV:
        ok &= np.isfinite(df["ev"].to_numpy(dtype=float))
    return df.loc[ok]


def dados_do_modelo(painel, prev, alvo, data, bloco):
    """Reconstroi treino e teste do modelo (alvo, data, bloco) exatamente como a Parte 2:
    painel do mes + blocos_AAAAMM.parquet + filtra_alvo; treino = blocos diferentes do teste e da validacao."""
    data = pd.Timestamp(data)
    blocos = pd.read_parquet(pasta_run() / f"blocos_{data:%Y%m}.parquet", columns=["ticker", "bloco"])
    pm = painel[painel["data"] == data].merge(blocos, on="ticker", how="inner")
    d = filtra_alvo(pm, alvo)
    treino = d[~d["bloco"].isin([bloco, bloco_validacao(bloco)])].reset_index(drop=True)
    teste = prev[(prev["alvo"] == alvo) & (prev["data"] == data) & (prev["bloco"] == bloco)].reset_index(drop=True)
    booster = carrega_modelo(alvo, data, bloco)
    X_tr = matriz_features(treino, booster)
    X_te = matriz_features(pm.set_index("ticker").loc[teste["ticker"]], booster)
    return booster, X_tr, treino[alvo].to_numpy(float), X_te, treino.rename(columns={alvo: "log_real"}), teste


# ------------------------------------------------------------------ retornos
def le_cotacao(arquivo, ticker_primeira_col="PETR4"):
    """Fechamento diario ajustado por proventos -> (ticker, data, preco). Aceita o .xlsx do Economatica
    (mesma regra de tickers do leitura.py) ou o cotacao_diaria.csv (data;TICKER1;TICKER2..., decimal ',')."""
    arquivo = Path(arquivo)
    if arquivo.suffix.lower() == ".csv":
        dados = pd.read_csv(arquivo, sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
        dados = dados.rename(columns={dados.columns[0]: "data"})
        dados["data"] = pd.to_datetime(dados["data"], dayfirst=True, errors="coerce")
    else:
        raw = pd.read_excel(arquivo, header=None, skiprows=3)
        cab, dados = raw.iloc[0], raw.iloc[1:].reset_index(drop=True)
        tickers = [ticker_primeira_col if i == 1 else str(c).split("\n")[-1].strip() for i, c in enumerate(cab) if i > 0]
        dados.columns = ["data"] + tickers
        dados["data"] = pd.to_datetime(dados["data"], errors="coerce")
    dados = dados.loc[:, ~pd.Index(dados.columns).duplicated()]
    longo = dados[dados["data"].notna()].melt(id_vars="data", var_name="ticker", value_name="preco")
    longo["preco"] = pd.to_numeric(longo["preco"], errors="coerce")
    return longo[longo["preco"] > 0]


def retornos_mensais(diario, folga_dias=4):
    """Preco do mes = ultimo fechamento do mes; ret = P_m / P_(m-1) - 1 so entre meses consecutivos.
    Descarta o ultimo mes se o export terminar no meio dele."""
    d = diario.sort_values(["ticker", "data"]).copy()
    d["mes"] = d["data"] + pd.offsets.MonthEnd(0)
    m = d.groupby(["ticker", "mes"], as_index=False).last()[["ticker", "mes", "preco"]].sort_values(["ticker", "mes"])
    ant = m.groupby("ticker")[["mes", "preco"]].shift()
    m["ret"] = np.where(ant["mes"] + pd.offsets.MonthEnd(1) == m["mes"], m["preco"] / ant["preco"] - 1, np.nan)
    r = m.dropna(subset=["ret"]).rename(columns={"mes": "data"})[["ticker", "data", "ret"]]
    ult = diario["data"].max()
    if (ult + pd.offsets.MonthEnd(0) - ult).days > folga_dias:
        r = r[r["data"] < ult + pd.offsets.MonthEnd(0)]
    return r.reset_index(drop=True)


def carrega_retornos(limite_extremo=3.0):
    """Usa retornos.parquet se existir; senao calcula a partir da cotacao (prefere o .xlsx, mais completo) e
    salva o parquet. Apague o retornos.parquet para recalcular."""
    if ARQ_RETORNOS.exists():
        return pd.read_parquet(ARQ_RETORNOS)
    fontes = [p for p in COTACOES_CANDIDATAS if p.exists()]
    if not fontes:
        raise FileNotFoundError(f"sem retornos.parquet e sem cotacao em {[str(p) for p in COTACOES_CANDIDATAS]}")
    r = retornos_mensais(cotacao_diaria())
    r.to_parquet(ARQ_RETORNOS)
    ext = r[r["ret"].abs() > limite_extremo].sort_values("ret", ascending=False)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    ext.to_csv(PASTA_SAIDA / "retornos_extremos.csv", index=False)
    print(f"retornos calculados de {fontes[0].name}: {len(r)} obs, {r.ticker.nunique()} tickers, "
          f"{r.data.min():%Y-%m} a {r.data.max():%Y-%m} | {len(ext)} com |ret| > {limite_extremo:.0%}")
    return r


_CACHE_DIARIO = {}


def cotacao_diaria():
    """Le a cotacao uma unica vez por execucao (retornos e liquidez usam a mesma leitura)."""
    if "d" not in _CACHE_DIARIO:
        fontes = [p for p in COTACOES_CANDIDATAS if p.exists()]
        if not fontes:
            raise FileNotFoundError(f"cotacao ausente em {[str(p) for p in COTACOES_CANDIDATAS]}")
        _CACHE_DIARIO["d"] = le_cotacao(fontes[0])
    return _CACHE_DIARIO["d"]


# ------------------------------------------------------------------ liquidez
def presenca_negociacao(diario, janela_meses=JANELA_LIQUIDEZ_MESES):
    """Para cada (ticker, mes t): fracao dos pregoes da janela [t-janela+1, t] em que a acao negociou.
    Pregao = dia com pelo menos uma acao cotada. Dia sem preco = dia sem negocio (como no export do Economatica).
    A janela comeca na primeira cotacao do ticker, para nao penalizar IPOs."""
    d = diario[["ticker", "data"]].copy()
    d["mes"] = d["data"] + pd.offsets.MonthEnd(0)
    pregoes = d.drop_duplicates("data").groupby("mes").size()
    negocios = d.groupby(["ticker", "mes"]).size()
    meses = pregoes.index
    linhas = []
    for ticker, s in negocios.groupby(level="ticker"):
        s = s.droplevel("ticker")
        idx = meses[(meses >= s.index.min()) & (meses <= s.index.max())]
        neg = s.reindex(idx, fill_value=0).rolling(janela_meses, min_periods=1).sum()
        preg = pregoes.reindex(idx).rolling(janela_meses, min_periods=1).sum()
        linhas.append(pd.DataFrame({"ticker": ticker, "data": idx, "presenca": (neg / preg).to_numpy(),
                                    "n_pregoes": preg.to_numpy()}))
    return pd.concat(linhas, ignore_index=True)


def carrega_liquidez():
    """liquidez.parquet se existir; senao calcula da cotacao e salva. Apague o arquivo para recalcular."""
    if ARQ_LIQUIDEZ.exists():
        return pd.read_parquet(ARQ_LIQUIDEZ)
    liq = presenca_negociacao(cotacao_diaria())
    liq.to_parquet(ARQ_LIQUIDEZ)
    return liq


def filtra_liquidez(df, liq, minima=PRESENCA_MINIMA, min_pregoes=MIN_PREGOES):
    """Mantem so (ticker, data) com presenca >= minima e historico >= min_pregoes. Sem cotacao = excluida."""
    if minima is None:
        return df.assign(liquida=True)
    m = df.merge(liq, on=["ticker", "data"], how="left")
    m["liquida"] = (m["presenca"] >= minima) & (m["n_pregoes"] >= min_pregoes)
    return m


# ------------------------------------------------------------------ fatores NEFIN
def le_fatores_nefin(fonte):
    """Arquivo MENSAL do NEFIN (year, month, Rm_minus_Rf, SMB, HML, WML, IML, Risk_Free; em fracao) ->
    data (fim do mes), rf, mkt (excesso sobre rf), smb, hml, wml, iml."""
    opcoes = {"storage_options": {"User-Agent": "Mozilla/5.0"}} if str(fonte).startswith("http") else {}
    f = pd.read_csv(fonte, **opcoes)
    f.columns = [str(c).strip() for c in f.columns]
    falt = {"year", "month", "Rm_minus_Rf", "SMB", "HML", "WML", "IML", "Risk_Free"} - set(f.columns)
    if falt:
        raise KeyError(f"arquivo do NEFIN sem as colunas {falt} (o formato mudou?)")
    out = pd.DataFrame({"data": pd.to_datetime(dict(year=f["year"], month=f["month"], day=1)) + pd.offsets.MonthEnd(0),
                        "rf": f["Risk_Free"], "mkt": f["Rm_minus_Rf"], "smb": f["SMB"], "hml": f["HML"],
                        "wml": f["WML"], "iml": f["IML"]})
    return out.dropna().reset_index(drop=True)


def carrega_fatores():
    """fatores.parquet se existir; senao le o NEFIN (arquivo local nefin_factors_monthly.csv ou download do site)
    e salva. Retorna None (sem alfas, rf = 0) se nao conseguir. Apague fatores.parquet para atualizar."""
    if ARQ_FATORES.exists():
        return pd.read_parquet(ARQ_FATORES)
    erros = []
    for fonte in ([ARQ_NEFIN_LOCAL] if ARQ_NEFIN_LOCAL.exists() else []) + [URL_NEFIN]:
        try:
            f = le_fatores_nefin(fonte)
            break
        except Exception as e:
            erros.append(f"{fonte}: {type(e).__name__}: {e}")
    else:
        warnings.warn("NEFIN: nao consegui obter os fatores.\n  " + "\n  ".join(erros) +
                      f"\n  Baixe nefin_factors_monthly.csv em nefin.com.br/data/risk-factors/ e ponha em {BASE_DADOS}."
                      " Carteiras seguem sem alfas e com rf = 0.")
        return None
    f.to_parquet(ARQ_FATORES)
    print(f"fatores NEFIN mensais: {f.data.min():%Y-%m} a {f.data.max():%Y-%m} ({len(f)} meses) -> {ARQ_FATORES.name}")
    return f


def colapsa_emissor(df, col_emissor="emissor"):
    """Uma linha por (emissor, data, alvo): fica a classe de maior valor de mercado. Sem coluna de emissor,
    usa a mesma heuristica do Parte2_treino.chave_emissor (4 letras iniciais do ticker)."""
    df = df.copy()
    if col_emissor not in df.columns:
        t = df["ticker"].astype(str)
        df[col_emissor] = t.str.extract(r"^([A-Za-z]{4})")[0].fillna(t)
    chaves = [col_emissor, "data"] + (["alvo"] if "alvo" in df.columns else [])
    df = df.sort_values(chaves + ["valor_mercado"], ascending=[True] * len(chaves) + [False])
    return df.drop_duplicates(chaves, keep="first")
