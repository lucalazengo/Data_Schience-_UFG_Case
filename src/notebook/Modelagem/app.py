import os
import csv
import unicodedata as ud
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    average_precision_score, roc_curve, precision_recall_curve
)
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier

# ------------------------------
# ======= CONFIG INICIAL =======
# ------------------------------
st.set_page_config(page_title="Acidentes — Goiás/Goiânia", page_icon="🚗", layout="wide")

st.sidebar.title("⚙️ Configurações")
default_paths = [
    "./data/processed_data/base_acidente.csv",
    "../data/processed_data/base_acidente.csv",
    "../../data/processed_data/base_acidente.csv"
]
csv_path = st.sidebar.text_input(
    "Caminho do CSV consolidado",
    value=next((p for p in default_paths if os.path.exists(p)), default_paths[0])
)
st.sidebar.info("Se precisar, altere o caminho do arquivo consolidado (base_acidente.csv).")

# --------- RMG (normalizado) ----------
RMG_MUNICIPIOS_RAW = [
    "GOIÂNIA","APARECIDA DE GOIÂNIA","SENADOR CANEDO","TRINDADE",
    "GOIANÁPOLIS","TEREZÓPOLIS DE GOIÁS","HIDROLÂNDIA","ABADIA DE GOIÁS",
    "GUAPÓ","NOVA VENEZA"
]

def _norm_str(s: pd.Series) -> pd.Series:
    return (s.astype(str)
              .str.upper()
              .apply(lambda x: ud.normalize("NFKD", x).encode("ASCII","ignore").decode("utf-8"))
              .str.strip())

RMG_MUNICIPIOS_NORM = set(_norm_str(pd.Series(RMG_MUNICIPIOS_RAW)).tolist())

# ------------------------------
# ====== FUNÇÕES AUXILIARES ====
# ------------------------------
@st.cache_data(show_spinner=False)
def load_csv_safe(path: str) -> pd.DataFrame:
    """Leitura robusta com detecção de separador e fallback de engine."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    # Detecta separador
    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(2048)
        try:
            dialect = csv.Sniffer().sniff(sample)
            sep = dialect.delimiter
        except csv.Error:
            sep = ","
    st.info(f"Separador detectado: '{sep}'")

    # 1) Tenta engine Python (aceita on_bad_lines='skip')
    try:
        return pd.read_csv(
            path, sep=sep, encoding="utf-8",
            engine="python", on_bad_lines="skip"
        )
    except Exception as e1:
        st.warning(f"Parser 'python' falhou ({e1.__class__.__name__}). Tentando engine 'c'...")
        # 2) Fallback para engine C (sem on_bad_lines)
        try:
            return pd.read_csv(
                path, sep=sep, encoding="utf-8",
                engine="c"  # não usar low_memory com 'python'; aqui o 'c' ignora on_bad_lines
            )
        except Exception as e2:
            st.error(f"Falha ao ler CSV com ambos parsers: {e2}")
            raise e2

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = load_csv_safe(path)
    st.success(f"Arquivo carregado com sucesso! {len(df)} linhas, {len(df.columns)} colunas.")

    # Normalização de textos
    for c in ["uf","municipio","tipo_acidente","causa_acidente","tipo_pista","tracado_via","uso_solo","dia_semana"]:
        if c in df.columns:
            df[c] = _norm_str(df[c])

    if "municipio" in df.columns:
        df["municipio_norm"] = df["municipio"]

    # Datas e tempo
    if "data_inversa" in df.columns:
        df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
        df["year"] = df["data_inversa"].dt.year
        df["month"] = df["data_inversa"].dt.month
        df["weekday"] = df["data_inversa"].dt.dayofweek

    if "horario" in df.columns:
        df["horario"] = pd.to_datetime(df["horario"], errors="coerce")
        df["HORA"] = df["horario"].dt.hour.fillna(-1).astype(int)

    # Numéricos com vírgula
    for c in ["km","latitude","longitude"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "."), errors="coerce")

    # Feridos totais
    if "TOTAL_FERIDOS" not in df.columns:
        df["TOTAL_FERIDOS"] = df.get("feridos_leves", 0).fillna(0) + df.get("feridos_graves", 0).fillna(0)

    # Inteiros base
    for c in ["mortos","veiculos","pessoas"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # Período do dia
    if "HORA" in df.columns:
        bins = [-1, 4, 11, 17, 23]
        labels = ["MADRUGADA","MANHA","TARDE","NOITE"]
        df["PERIODO_DIA"] = pd.cut(df["HORA"], bins=bins, labels=labels, include_lowest=True)
        df["PERIODO_DIA"] = df["PERIODO_DIA"].cat.add_categories(["DESCONHECIDO"])
        df.loc[(df["HORA"]<0)|(df["HORA"]>23), "PERIODO_DIA"] = "DESCONHECIDO"
    else:
        df["PERIODO_DIA"] = "DESCONHECIDO"

    # Taxa de mortalidade (defensiva)
    if "pessoas" in df.columns and "mortos" in df.columns:
        df["TAXA_MORTALIDADE"] = (df["mortos"] / df["pessoas"].replace(0, np.nan)).fillna(0)
    else:
        df["TAXA_MORTALIDADE"] = 0.0

    return df

@st.cache_data(show_spinner=False)
def subset_go_rmg(df: pd.DataFrame):
    df_go = df[df.get("uf","") == "GO"].copy()
    if "municipio_norm" not in df_go.columns and "municipio" in df_go.columns:
        df_go["municipio_norm"] = _norm_str(df_go["municipio"])
    df_rmg = df_go[df_go["municipio_norm"].isin(RMG_MUNICIPIOS_NORM)].copy()
    return df_go, df_rmg

def kpis_bloco(df, titulo):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Registros", f"{len(df):,}".replace(",",".")) 
    with col2: st.metric("Mortos", int(df.get("mortos",0).sum()))
    with col3: st.metric("Feridos (L+G)", int(df.get("TOTAL_FERIDOS",0).sum()))
    taxa = (df.get("mortos",pd.Series([0])).sum()/max(len(df),1)*100)
    with col4: st.metric("Taxa bruta por ocorrência", f"{taxa:.2f}%")
    st.caption(titulo)

def plot_tendencias(ag_go, ag_rmg):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ag_go["year"], y=ag_go["oc"], name="GO — ocorrências", mode="lines+markers"))
    if len(ag_rmg):
        fig.add_trace(go.Scatter(x=ag_rmg["year"], y=ag_rmg["oc"], name="RMG — ocorrências", mode="lines+markers"))
    fig.update_layout(title="Ocorrências por ano", template="plotly_white", height=350)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ag_go["year"], y=ag_go["mt"], name="GO — mortos", mode="lines+markers"))
    if len(ag_rmg):
        fig2.add_trace(go.Scatter(x=ag_rmg["year"], y=ag_rmg["mt"], name="RMG — mortos", mode="lines+markers"))
    fig2.update_layout(title="Mortes por ano", template="plotly_white", height=350)

    c1,c2=st.columns(2)
    with c1: st.plotly_chart(fig,use_container_width=True)
    with c2: st.plotly_chart(fig2,use_container_width=True)

def indice_periculosidade(df):
    g=df.groupby("br", dropna=True).agg(oc=("br","size"),mt=("mortos","sum")).reset_index()
    if len(g)==0: return g.assign(indice=0.0,taxa=0.0)
    g["taxa"]=g["mt"]/g["oc"].replace(0,np.nan)
    g["indice"]=(0.4*(g["oc"]/max(g["oc"].max(),1)) + 0.6*(g["mt"]/max(g["mt"].max(),1)))*10
    return g.sort_values("indice",ascending=False)

def plot_top_brs(g,top=20):
    fig=px.bar(g.head(top),x="br",y="indice",text_auto=".2f",
               title="TOP BRs por índice de periculosidade (GO)",labels={"indice":"Índice (0–10)","br":"BR"})
    fig.update_layout(template="plotly_white",height=420)
    st.plotly_chart(fig,use_container_width=True)

# -------------------------------
# ============ MODELAGEM =========
# -------------------------------
def make_splits(df_escopo):
    y=(df_escopo["mortos"]>0).astype(int)

    num=["km","veiculos","pessoas","TOTAL_FERIDOS","HORA"]
    num=[c for c in num if c in df_escopo.columns]

    cat=["tipo_acidente","causa_acidente","tipo_pista","tracado_via","uso_solo",
         "PERIODO_DIA","dia_semana","municipio","br"]
    cat=[c for c in cat if c in df_escopo.columns]

    X=df_escopo[num+cat].copy()
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25,random_state=42,stratify=y)

    ct=ColumnTransformer([
        ("num","passthrough",num),
        ("cat",OneHotEncoder(handle_unknown="ignore",sparse_output=False),cat)
    ], remainder="drop", verbose_feature_names_out=False)

    meta={"num_features":num,"cat_features":cat}
    return X_train,X_test,y_train,y_test,ct,meta

def build_models(ct):
    lr=LogisticRegression(max_iter=1000,class_weight="balanced")
    pipe_lr=Pipeline([("prep",ct),("clf",lr)])

    hgb=HistGradientBoostingClassifier(learning_rate=0.08,min_samples_leaf=20,random_state=42)
    pipe_hgb=Pipeline([("prep",ct),("clf",hgb)])

    rf=RandomForestClassifier(
        n_estimators=300, max_depth=None, min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=-1
    )
    pipe_rf=Pipeline([("prep",ct),("clf",rf)])

    return {"LogisticRegression":pipe_lr, "HistGradientBoosting":pipe_hgb, "RandomForest":pipe_rf}

def find_best_threshold(y_true, proba, beta=2.0):
    ts = np.linspace(0.05, 0.95, 91)
    best_t, best_f = 0.5, -1
    for t in ts:
        pred = (proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
        precision = tp / (tp + fp + 1e-9)
        recall    = tp / (tp + fn + 1e-9)
        fbeta = (1+beta**2) * (precision*recall) / (beta**2*precision + recall + 1e-9)
        if fbeta > best_f: best_f, best_t = fbeta, t
    return best_t, best_f

def plot_roc_pr(y_test, proba, title_suffix=""):
    fpr, tpr, _ = roc_curve(y_test, proba)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name="ROC"))
    fig1.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines", name="baseline", line=dict(dash="dash")))
    fig1.update_layout(title=f"Curva ROC {title_suffix}", xaxis_title="FPR", yaxis_title="TPR", template="plotly_white", height=360)

    prec, rec, _ = precision_recall_curve(y_test, proba)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=rec, y=prec, mode="lines", name="PR"))
    fig2.update_layout(title=f"Curva Precisão-Recall {title_suffix}", xaxis_title="Recall", yaxis_title="Precisão", template="plotly_white", height=360)
    return fig1, fig2

def evaluate_model(name, pipe, X_test, y_test):
    proba = pipe.predict_proba(X_test)[:,1]
    pred  = (proba >= 0.5).astype(int)
    roc = roc_auc_score(y_test, proba)
    ap  = average_precision_score(y_test, proba)

    st.markdown(f"### {name}")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("ROC-AUC", f"{roc:.3f}")
    with c2: st.metric("PR-AUC (AP)", f"{ap:.3f}")
    with c3:
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        st.metric("Recall (classe 1)", f"{(tp/(tp+fn+1e-9)):.3f}")

    cm = confusion_matrix(y_test, pred)
    fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale="Blues",
                       labels=dict(x="Predito", y="Real", color="Qtd"),
                       x=["0","1"], y=["0","1"], title="Matriz de confusão (limiar 0.5)")
    st.plotly_chart(fig_cm, use_container_width=True)
    st.text(classification_report(y_test, pred, digits=3))

    fig_roc, fig_pr = plot_roc_pr(y_test, proba, title_suffix=f"— {name}")
    cA, cB = st.columns(2)
    with cA: st.plotly_chart(fig_roc, use_container_width=True)
    with cB: st.plotly_chart(fig_pr, use_container_width=True)

    best_t, best_f = find_best_threshold(y_test, proba, beta=2.0)
    pred_opt = (proba >= best_t).astype(int)
    cm_opt = confusion_matrix(y_test, pred_opt)
    fig_cm_opt = px.imshow(cm_opt, text_auto=True, color_continuous_scale="Purples",
                           labels=dict(x="Predito", y="Real", color="Qtd"),
                           x=["0","1"], y=["0","1"], title=f"Matriz (limiar ótimo F2 = {best_t:.2f})")
    st.plotly_chart(fig_cm_opt, use_container_width=True)
    st.info(f"**Limiar ótimo (F2)**: {best_t:.2f} | **F2** = {best_f:.3f}")

    return proba, ap

def show_permutation_importance(best_name, best_pipe, X_test, y_test, feature_names_original, top=25):
    with st.spinner("Calculando importância por permutação..."):
        perm = permutation_importance(best_pipe, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
    imp = pd.Series(perm.importances_mean, index=feature_names_original).sort_values(ascending=False).head(top).reset_index()
    imp.columns = ["feature","importance"]
    fig = px.bar(imp, x="importance", y="feature", orientation="h",
                 title=f"Top {top} — Importância (Permutation) • {best_name}",
                 labels={"importance":"Impacto (↓ acurácia)","feature":"Feature"})
    fig.update_layout(template="plotly_white", height=520)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# ======== EXECUÇÃO APP ========
# -------------------------------
try:
    base = load_data(csv_path)
except Exception as e:
    st.error(str(e))
    st.stop()

df_go, df_rmg = subset_go_rmg(base)

st.title("🚗 Acidentes em Rodovias — Goiás / Goiânia")
st.caption("Dashboard analítico para GO e Região Metropolitana de Goiânia (RMG): tendências, hotspots e modelagem da severidade (fatais).")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "📈 Tendências", "🗺️ Hotspots & BRs", "🤖 Modelagem"])

# ====== TAB 1 ======
with tab1:
    st.subheader("KPIs — Estado de Goiás (GO)")
    kpis_bloco(df_go, "Resumo geral para a UF GO")
    st.markdown("---")

    st.subheader("Maiores municípios (GO) por nº de ocorrências")
    if len(df_go):
        top_mun = df_go["municipio"].value_counts().head(30).rename_axis("municipio").reset_index(name="ocorrencias")
        fig = px.bar(top_mun, y="municipio", x="ocorrencias", orientation="h", height=650, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem registros para GO no arquivo.")

# ====== TAB 2 ======
with tab2:
    st.subheader("Tendências — GO x RMG")
    ag_go = df_go.groupby("year", dropna=True).agg(oc=("year","size"), mt=("mortos","sum")).reset_index()
    ag_rmg = df_rmg.groupby("year", dropna=True).agg(oc=("year","size"), mt=("mortos","sum")).reset_index()

    if len(df_rmg) == 0:
        st.warning("⚠️ A RMG apareceu zerada. Normalizei acentos/caixa; se ainda zerar, verifique se o CSV contém municípios da RMG.")
    plot_tendencias(ag_go, ag_rmg)

    st.markdown("---")
    st.subheader("Sazonalidade — GO")
    by_month = df_go.groupby("month", dropna=True).agg(oc=("month","size"), mt=("mortos","sum")).reset_index()
    c1, c2 = st.columns(2)
    with c1:
        figm = px.bar(by_month, x="month", y="oc", title="Ocorrências por mês", template="plotly_white")
        st.plotly_chart(figm, use_container_width=True)
    with c2:
        figm2 = px.bar(by_month, x="month", y="mt", title="Mortes por mês", template="plotly_white", color="mt", color_continuous_scale="Reds")
        st.plotly_chart(figm2, use_container_width=True)

# ====== TAB 3 ======
with tab3:
    st.subheader("Hotspots e trechos críticos (índice de periculosidade)")
    g = indice_periculosidade(df_go)
    if len(g):
        plot_top_brs(g, top=25)
        st.caption("Índice combina **volume** (0.4) e **severidade** (0.6) em escala 0–10.")
    else:
        st.warning("Sem dados suficientes para calcular o índice.")

# ====== TAB 4 (MODELAGEM) ======
with tab4:
    st.subheader("Escopo da modelagem")
    escopo = st.radio("Escolha o conjunto para treinar/avaliar:", ["GO (Estado)", "RMG (Região Metropolitana)"], horizontal=True)
    df_escopo = df_go if escopo.startswith("GO") else df_rmg

    if len(df_escopo) == 0 or (df_escopo["mortos"]>0).sum() == 0:
        st.warning("Sem dados ou positivos (mortos>0) suficientes no escopo selecionado.")
    else:
        X_train, X_test, y_train, y_test, ct, meta = make_splits(df_escopo)
        st.write(f"**Treino:** {len(X_train):,} | **Teste:** {len(X_test):,} | **Positivos no teste:** {int(y_test.sum())} ({y_test.mean()*100:.2f}%)".replace(",", "."))

        st.subheader("Treino e avaliação")
        models = build_models(ct)
        all_probas, all_aps = {}, {}

        for name, pipe in models.items():
            with st.spinner(f"Treinando {name}..."):
                pipe.fit(X_train, y_train)
            proba, ap = evaluate_model(name, pipe, X_test, y_test)
            all_probas[name] = proba
            all_aps[name] = ap
            st.markdown("---")

        # Importância (Permutation) com o melhor modelo por AP
        best_name = max(all_aps, key=all_aps.get)
        st.subheader(f"Importância de features — {best_name}")
        feature_names_original = meta["num_features"] + meta["cat_features"]
        show_permutation_importance(best_name, models[best_name], X_test, y_test, feature_names_original, top=25)

st.markdown("---")
st.caption("Feito por Manuel e Willgnner")
