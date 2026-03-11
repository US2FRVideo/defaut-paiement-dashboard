import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Défaut Paiement",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Tableau de bord interactif - Défaut de paiement")
st.write("Analyse du risque de défaut des clients détenteurs de cartes de crédit.")

# Chargement des données
df = pd.read_csv("data/training.csv", sep=None, engine="python")
df.columns = [str(col).strip().upper() for col in df.columns]

# Vérification minimale
required_cols = ["DEF", "PAY_1", "LIMIT_BAL", "SEX", "EDUCATION"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Colonnes manquantes : {missing}")
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

# Sidebar filtres
st.sidebar.header("Filtres interactifs")

sex_options = ["Tous"] + sorted(df["SEX"].dropna().astype(str).unique().tolist())
selected_sex = st.sidebar.selectbox("Sexe", sex_options)

edu_options = ["Tous"] + sorted(df["EDUCATION"].dropna().astype(str).unique().tolist())
selected_edu = st.sidebar.selectbox("Éducation", edu_options)

filtered_df = df.copy()

if selected_sex != "Tous":
    filtered_df = filtered_df[filtered_df["SEX"].astype(str) == selected_sex]

if selected_edu != "Tous":
    filtered_df = filtered_df[filtered_df["EDUCATION"].astype(str) == selected_edu]

# KPI
taux_defaut = filtered_df["DEF"].mean() * 100
nb_clients = len(filtered_df)

col1, col2 = st.columns(2)
col1.metric("Taux de défaut", f"{taux_defaut:.2f}%")
col2.metric("Nombre de clients", f"{nb_clients}")

st.divider()

# Graphique 1 : taux de défaut selon PAY_1
st.subheader("Impact de l'historique de paiement sur le défaut")

pay1_chart = (
    filtered_df.groupby("PAY_1", as_index=False)["DEF"]
    .mean()
    .sort_values("PAY_1")
)

fig1 = px.bar(
    pay1_chart,
    x="PAY_1",
    y="DEF",
    labels={"PAY_1": "Historique de paiement (PAY_1)", "DEF": "Taux de défaut"}
)
fig1.update_layout(yaxis_tickformat=".0%")

st.plotly_chart(fig1, use_container_width=True)

# Graphique 2 : taux de défaut selon LIMIT_BAL
st.subheader("Impact de la limite de crédit sur le défaut")

filtered_df["LIMIT_BIN"] = pd.cut(filtered_df["LIMIT_BAL"], bins=10)
limit_chart = (
    filtered_df.groupby("LIMIT_BIN", as_index=False)["DEF"]
    .mean()
)

# Conversion en texte pour éviter l'erreur JSON/Plotly
limit_chart["LIMIT_BIN"] = limit_chart["LIMIT_BIN"].astype(str)

fig2 = px.bar(
    limit_chart,
    x="LIMIT_BIN",
    y="DEF",
    labels={"LIMIT_BIN": "Tranches de limite de crédit", "DEF": "Taux de défaut"}
)
fig2.update_layout(
    yaxis_tickformat=".0%",
    xaxis_tickangle=-45
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Lecture décisionnelle")
st.write(
    """
- Le taux de défaut global permet d’évaluer rapidement le niveau de risque du portefeuille client.
- L’historique de paiement (PAY_1) est le facteur le plus important : plus le retard récent augmente, plus le risque de défaut augmente.
- La limite de crédit permet d’identifier des profils financiers plus ou moins risqués.
- Les filtres interactifs permettent à la direction commerciale d’analyser des segments spécifiques de clients.
"""
)
