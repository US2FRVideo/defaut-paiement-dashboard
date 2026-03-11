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
required_cols = ["DEF", "PAY_1", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Colonnes manquantes : {missing}")
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

# ------------------------------
# Transformation des codes en libellés métier
# ------------------------------

sex_map = {
    1: "Homme",
    2: "Femme"
}

education_map = {
    1: "École supérieure",
    2: "Université",
    3: "Lycée",
    4: "Autres",
    5: "Autres",
    6: "Autres",
    0: "Autres"
}

marriage_map = {
    1: "Marié",
    2: "Célibataire",
    3: "Autres",
    0: "Autres"
}

df["SEX_LABEL"] = df["SEX"].map(sex_map).fillna("Autres")
df["EDUCATION_LABEL"] = df["EDUCATION"].map(education_map).fillna("Autres")
df["MARRIAGE_LABEL"] = df["MARRIAGE"].map(marriage_map).fillna("Autres")

df["AGE_GROUP"] = pd.cut(
    df["AGE"],
    bins=[20, 30, 40, 50, 60, 80],
    labels=["21-30 ans", "31-40 ans", "41-50 ans", "51-60 ans", "61-79 ans"],
    include_lowest=True
)

# ------------------------------
# Sidebar filtres
# ------------------------------

st.sidebar.header("Filtres interactifs")

filtered_df = df.copy()

sex_options = ["Tous"] + sorted(df["SEX_LABEL"].dropna().unique().tolist())
selected_sex = st.sidebar.selectbox("Sexe", sex_options)

edu_options = ["Tous"] + sorted(df["EDUCATION_LABEL"].dropna().unique().tolist())
selected_edu = st.sidebar.selectbox("Niveau d'éducation", edu_options)

marriage_options = ["Tous"] + sorted(df["MARRIAGE_LABEL"].dropna().unique().tolist())
selected_marriage = st.sidebar.selectbox("Situation matrimoniale", marriage_options)

age_options = ["Tous"] + [str(x) for x in df["AGE_GROUP"].dropna().unique().tolist()]
selected_age = st.sidebar.selectbox("Tranche d'âge", age_options)

if selected_sex != "Tous":
    filtered_df = filtered_df[filtered_df["SEX_LABEL"] == selected_sex]

if selected_edu != "Tous":
    filtered_df = filtered_df[filtered_df["EDUCATION_LABEL"] == selected_edu]

if selected_marriage != "Tous":
    filtered_df = filtered_df[filtered_df["MARRIAGE_LABEL"] == selected_marriage]

if selected_age != "Tous":
    filtered_df = filtered_df[filtered_df["AGE_GROUP"].astype(str) == selected_age]

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

# Graphique 3 : taux de défaut selon le sexe
st.subheader("Taux de défaut selon le sexe")

sex_chart = (
    filtered_df.groupby("SEX_LABEL", as_index=False)["DEF"]
    .mean()
    .sort_values("SEX_LABEL")
)

fig3 = px.bar(
    sex_chart,
    x="SEX_LABEL",
    y="DEF",
    labels={"SEX_LABEL": "Sexe", "DEF": "Taux de défaut"}
)
fig3.update_layout(yaxis_tickformat=".0%")

st.plotly_chart(fig3, use_container_width=True)

# Graphique 4 : taux de défaut selon le niveau d'éducation
st.subheader("Taux de défaut selon le niveau d'éducation")

edu_chart = (
    filtered_df.groupby("EDUCATION_LABEL", as_index=False)["DEF"]
    .mean()
)

fig4 = px.bar(
    edu_chart,
    x="EDUCATION_LABEL",
    y="DEF",
    labels={"EDUCATION_LABEL": "Niveau d'éducation", "DEF": "Taux de défaut"}
)
fig4.update_layout(yaxis_tickformat=".0%")

st.plotly_chart(fig4, use_container_width=True)

# Graphique 5 : répartition des clients par tranche d'âge
st.subheader("Répartition des clients par tranche d'âge")

age_chart = (
    filtered_df.groupby("AGE_GROUP", as_index=False)
    .size()
)

fig5 = px.bar(
    age_chart,
    x="AGE_GROUP",
    y="size",
    labels={"AGE_GROUP": "Tranche d'âge", "size": "Nombre de clients"}
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()

st.subheader("Lecture décisionnelle")
st.write(
    """
- Le taux de défaut global permet d’évaluer rapidement le niveau de risque du portefeuille client.
- L’historique de paiement (PAY_1) est le facteur le plus important : plus le retard récent augmente, plus le risque de défaut augmente.
- La limite de crédit permet d’identifier des profils financiers plus ou moins risqués.
- Les graphiques complémentaires permettent d’analyser le risque selon le sexe, le niveau d’éducation et la tranche d’âge.
- Les filtres interactifs permettent à la direction commerciale d’analyser des segments spécifiques de clients.
"""
)
