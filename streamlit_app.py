import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Défaut Paiement", page_icon="💳", layout="wide")

st.title("💳 Tableau de bord interactif - Défaut de paiement")

st.write("Analyse du risque de défaut des clients détenteurs de cartes de crédit.")

# Charger les données
df = pd.read_csv("data/training.csv")

# KPI
taux_defaut = df["DEF"].mean()
nb_clients = len(df)

col1, col2 = st.columns(2)

col1.metric("Taux de défaut", f"{taux_defaut:.2%}")
col2.metric("Nombre de clients", nb_clients)

st.divider()

# Graphique PAY_1
st.subheader("Impact de l'historique de paiement sur le défaut")

pay1 = df.groupby("PAY_1")["DEF"].mean().reset_index()

fig1 = px.bar(pay1, x="PAY_1", y="DEF")
st.plotly_chart(fig1, use_container_width=True)

# Graphique LIMIT_BAL
st.subheader("Impact de la limite de crédit")

df["LIMIT_BIN"] = pd.cut(df["LIMIT_BAL"], bins=10)

limit_chart = df.groupby("LIMIT_BIN")["DEF"].mean().reset_index()

fig2 = px.bar(limit_chart, x="LIMIT_BIN", y="DEF")

st.plotly_chart(fig2, use_container_width=True)

# Filtres
st.sidebar.header("Filtres")

sex = st.sidebar.selectbox("Sexe", ["Tous"] + sorted(df["SEX"].unique().tolist()))

if sex != "Tous":
    df = df[df["SEX"] == sex]
