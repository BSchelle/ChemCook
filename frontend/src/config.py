# Configuration globale et Styles CSS pour le Frontend ChemCook

DEFAULT_API_URL = " http://127.0.0.1:8000/api/v1/calculations/preview"

# Styles CSS personnalisés pour masquer l'aspect Streamlit brut et donner un rendu premium "portfolio"
CUSTOM_CSS = """
<style>
    /* Police et fond global de l'application */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #090b0f;
    }

    .main {
        background-color: #090b0f;
        color: #e2e8f0;
    }

    /* Barre latérale (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #0f1219 !important;
        border-right: 1px solid #1a202c !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSubheader"] {
        color: #94a3b8 !important;
    }

    /* Cartes de Métriques (st.metric) */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 18px 22px !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(45, 212, 191, 0.25);
        box-shadow: 0 15px 35px -10px rgba(45, 212, 191, 0.1);
    }

    div[data-testid="stMetricLabel"] > div {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] > div {
        color: #2dd4bf !important;
        font-weight: 700;
        font-size: 1.9rem !important;
        letter-spacing: -0.02em;
    }

    /* En-têtes, Titres et Sous-titres */
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(135deg, #38bdf8, #2dd4bf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        padding-bottom: 0.5rem;
    }

    h2, h3 {
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        padding-bottom: 10px;
        margin-top: 2rem !important;
        letter-spacing: -0.01em;
    }

    /* Style des boutons (st.button) */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7, #0f766e) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 20px -5px rgba(15, 118, 110, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100%;
        margin-top: 10px;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px -5px rgba(15, 118, 110, 0.6) !important;
        background: linear-gradient(135deg, #0369a1, #115e59) !important;
    }

    .stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Tableaux de données (st.data_editor et st.dataframe) */
    div[data-testid="stDataFrameResizer"] {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-color: rgba(15, 23, 42, 0.4) !important;
    }

    /* Badge de rôle personnalisé pour affichage HTML dans la table de résultats */
    .role-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .role-reactant { background-color: rgba(45, 212, 191, 0.12); color: #2dd4bf; border: 1px solid rgba(45, 212, 191, 0.2); }
    .role-product { background-color: rgba(245, 158, 11, 0.12); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
    .role-solvent { background-color: rgba(168, 85, 247, 0.12); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.2); }
    .role-catalyst { background-color: rgba(236, 72, 153, 0.12); color: #ec4899; border: 1px solid rgba(236, 72, 153, 0.2); }
    .role-additive { background-color: rgba(100, 116, 139, 0.12); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.2); }

    /* Ajustement des inputs textuels de Streamlit */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #2dd4bf !important;
    }
</style>
"""
