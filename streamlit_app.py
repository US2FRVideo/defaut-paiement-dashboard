import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="Dashboard Défaut Paiement",
    page_icon="💳",
    layout="wide"
)

# ==============================
# STYLE
# ==============================
st.markdown("""
<style>
    .main {
        background-color: #0b1020;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: white !important;
    }
    .kpi-card {
        background: linear-gradient(135deg, #182848 0%, #4b6cb7 100%);
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-card h3 {
        margin: 0;
        font-size: 1rem;
        color: #dbeafe !important;
    }
    .kpi-card p {
        margin: 8px 0 0 0;
        font-size: 2rem;
        font-weight: 700;
        color: white !important;
    }
    .section-box {
        background-color: rgba(255,255,255,0.03);
        padding: 14px 18px;
        border-radius: 18px;
        margin-bottom: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# DATA
# ==============================
df = pd.read_csv("data/training.csv", sep=None, engine="python")
df.columns = [str(col).strip().upper() for col in df.columns]

required_cols = ["DEF", "PAY_1", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE", "BILL_AMT1"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Colonnes manquantes : {missing}")
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

# ==============================
# LABELS METIER
# ==============================
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
df["DEF_LABEL"] = df["DEF"].map({0: "Pas de défaut", 1: "Défaut"}).fillna("Inconnu")

df["AGE_GROUP"] = pd.cut(
    df["AGE"],
    bins=[20, 30, 40, 50, 60, 80],
    labels=["21-30 ans", "31-40 ans", "41-50 ans", "51-60 ans", "61-79 ans"],
    include_lowest=True
)

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.title("🎛️ Filtres interactifs")

sex_options = sorted(df["SEX_LABEL"].dropna().unique().tolist())
selected_sex = st.sidebar.multiselect("Sexe", sex_options, default=sex_options)

edu_options = sorted(df["EDUCATION_LABEL"].dropna().unique().tolist())
selected_edu = st.sidebar.multiselect("Niveau d'éducation", edu_options, default=edu_options)

marriage_options = sorted(df["MARRIAGE_LABEL"].dropna().unique().tolist())
selected_marriage = st.sidebar.multiselect("Situation matrimoniale", marriage_options, default=marriage_options)

age_options = [str(x) for x in df["AGE_GROUP"].dropna().unique().tolist()]
selected_age = st.sidebar.multiselect("Tranche d'âge", age_options, default=age_options)

default_options = sorted(df["DEF_LABEL"].dropna().unique().tolist())
selected_default = st.sidebar.multiselect("Statut de défaut", default_options, default=default_options)

filtered_df = df.copy()
filtered_df = filtered_df[filtered_df["SEX_LABEL"].isin(selected_sex)]
filtered_df = filtered_df[filtered_df["EDUCATION_LABEL"].isin(selected_edu)]
filtered_df = filtered_df[filtered_df["MARRIAGE_LABEL"].isin(selected_marriage)]
filtered_df = filtered_df[filtered_df["AGE_GROUP"].astype(str).isin(selected_age)]
filtered_df = filtered_df[filtered_df["DEF_LABEL"].isin(selected_default)]

if filtered_df.empty:
    st.warning("Aucune donnée disponible avec ces filtres.")
    st.stop()

# ==============================
# HELPERS
# ==============================
template = "plotly_dark"
color_main = "#60a5fa"
color_second = "#f59e0b"
color_third = "#34d399"
color_fourth = "#f472b6"
color_red = "#ef4444"

# ==============================
# HEADER
# ==============================
st.markdown("<h1 style='text-align:center;'>💳 DASHBOARD KPI – DÉFAUT DE PAIEMENT</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Pilotage du risque client pour la direction commerciale</p>",
    unsafe_allow_html=True
)

# ==============================
# KPI
# ==============================
taux_defaut = filtered_df["DEF"].mean() * 100
nb_clients = len(filtered_df)
limit_moyenne = filtered_df["LIMIT_BAL"].mean()
age_moyen = filtered_df["AGE"].mean()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3>Taux de défaut</h3>
            <p>{taux_defaut:.2f}%</p>
        </div>
        """, unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3>Nombre de clients</h3>
            <p>{nb_clients}</p>
        </div>
        """, unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3>Limite de crédit moyenne</h3>
            <p>{limit_moyenne:,.0f}</p>
        </div>
        """, unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3>Âge moyen</h3>
            <p>{age_moyen:.1f} ans</p>
        </div>
        """, unsafe_allow_html=True
    )

st.markdown("---")

# ==============================
# TABS
# ==============================
tab1, tab2, tab3 = st.tabs(["📊 Vue globale", "👥 Segmentation", "📈 Analyse avancée"])

# ==============================
# TAB 1 - VUE GLOBALE
# ==============================
with tab1:
    row1_col1, row1_col2 = st.columns([1.2, 1])

    with row1_col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Impact de l’historique de paiement sur le taux de défaut")
        pay1_chart = (
            filtered_df.groupby("PAY_1", as_index=False)["DEF"]
            .mean()
            .sort_values("PAY_1")
        )
        fig1 = px.bar(
            pay1_chart,
            x="PAY_1",
            y="DEF",
            text_auto=".0%",
            color_discrete_sequence=[color_main],
            labels={"PAY_1": "Historique de paiement (PAY_1)", "DEF": "Taux de défaut"},
            template=template
        )
        fig1.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_col2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Répartition du portefeuille")
        donut_data = filtered_df["DEF_LABEL"].value_counts().reset_index()
        donut_data.columns = ["Statut", "Nombre"]
        fig_donut = px.pie(
            donut_data,
            names="Statut",
            values="Nombre",
            hole=0.6,
            color="Statut",
            color_discrete_map={"Défaut": color_red, "Pas de défaut": color_third},
            template=template
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Impact de la limite de crédit sur le taux de défaut")
        limit_df = filtered_df.copy()
        limit_df["LIMIT_BIN"] = pd.cut(limit_df["LIMIT_BAL"], bins=10)
        limit_chart = (
            limit_df.groupby("LIMIT_BIN", as_index=False)["DEF"]
            .mean()
        )
        limit_chart["LIMIT_BIN"] = limit_chart["LIMIT_BIN"].astype(str)
        fig2 = px.line(
            limit_chart,
            x="LIMIT_BIN",
            y="DEF",
            markers=True,
            color_discrete_sequence=[color_second],
            labels={"LIMIT_BIN": "Tranches de limite de crédit", "DEF": "Taux de défaut"},
            template=template
        )
        fig2.update_layout(yaxis_tickformat=".0%", xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_col2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Distribution de l’âge")
        fig_age = px.histogram(
            filtered_df,
            x="AGE",
            nbins=20,
            color_discrete_sequence=[color_third],
            labels={"AGE": "Âge"},
            template=template
        )
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# TAB 2 - SEGMENTATION
# ==============================
with tab2:
    seg_col1, seg_col2 = st.columns(2)

    with seg_col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Taux de défaut selon le sexe")
        sex_chart = (
            filtered_df.groupby("SEX_LABEL", as_index=False)["DEF"]
            .mean()
        )
        fig3 = px.bar(
            sex_chart,
            x="SEX_LABEL",
            y="DEF",
            text_auto=".0%",
            color="SEX_LABEL",
            color_discrete_sequence=[color_main, color_fourth],
            labels={"SEX_LABEL": "Sexe", "DEF": "Taux de défaut"},
            template=template
        )
        fig3.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with seg_col2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Taux de défaut selon le niveau d’éducation")
        edu_chart = (
            filtered_df.groupby("EDUCATION_LABEL", as_index=False)["DEF"]
            .mean()
        )
        fig4 = px.bar(
            edu_chart,
            x="EDUCATION_LABEL",
            y="DEF",
            text_auto=".0%",
            color="EDUCATION_LABEL",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"EDUCATION_LABEL": "Niveau d'éducation", "DEF": "Taux de défaut"},
            template=template
        )
        fig4.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    seg_col3, seg_col4 = st.columns(2)

    with seg_col3:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Taux de défaut selon la situation matrimoniale")
        marriage_chart = (
            filtered_df.groupby("MARRIAGE_LABEL", as_index=False)["DEF"]
            .mean()
        )
        fig5 = px.bar(
            marriage_chart,
            x="MARRIAGE_LABEL",
            y="DEF",
            text_auto=".0%",
            color="MARRIAGE_LABEL",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"MARRIAGE_LABEL": "Situation matrimoniale", "DEF": "Taux de défaut"},
            template=template
        )
        fig5.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with seg_col4:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Taux de défaut selon la tranche d’âge")
        age_default_chart = (
            filtered_df.groupby("AGE_GROUP", as_index=False)["DEF"]
            .mean()
        )
        age_default_chart["AGE_GROUP"] = age_default_chart["AGE_GROUP"].astype(str)
        fig6 = px.line(
            age_default_chart,
            x="AGE_GROUP",
            y="DEF",
            markers=True,
            color_discrete_sequence=[color_fourth],
            labels={"AGE_GROUP": "Tranche d'âge", "DEF": "Taux de défaut"},
            template=template
        )
        fig6.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# TAB 3 - ANALYSE AVANCEE
# ==============================
with tab3:
    adv_col1, adv_col2 = st.columns(2)

    with adv_col1:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Relation entre limite de crédit et montant facturé")
        scatter_df = filtered_df.copy()
        fig7 = px.scatter(
            scatter_df,
            x="LIMIT_BAL",
            y="BILL_AMT1",
            color="DEF_LABEL",
            color_discrete_map={"Défaut": color_red, "Pas de défaut": color_main},
            opacity=0.6,
            labels={
                "LIMIT_BAL": "Limite de crédit",
                "BILL_AMT1": "Montant facturé",
                "DEF_LABEL": "Statut"
            },
            template=template
        )
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with adv_col2:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Boxplot des montants facturés selon le défaut")
        fig8 = px.box(
            filtered_df,
            x="DEF_LABEL",
            y="BILL_AMT1",
            color="DEF_LABEL",
            color_discrete_map={"Défaut": color_red, "Pas de défaut": color_third},
            labels={"DEF_LABEL": "Statut", "BILL_AMT1": "Montant facturé"},
            template=template
        )
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Lecture décisionnelle")
    st.write(
        """
- **Le taux de défaut global** mesure immédiatement le niveau de risque du portefeuille.
- **PAY_1** reste le signal d’alerte principal : plus le retard récent est élevé, plus le défaut augmente fortement.
- **La limite de crédit** et **les montants facturés** permettent de distinguer des profils plus ou moins risqués.
- **La segmentation** par sexe, éducation, situation matrimoniale et tranche d’âge améliore l’interprétation métier.
- Les **filtres interactifs** permettent à la direction commerciale d’explorer rapidement des sous-populations spécifiques.
"""
    )
    st.markdown("</div>", unsafe_allow_html=True)
