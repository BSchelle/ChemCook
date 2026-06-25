import streamlit as st
from src.config import CUSTOM_CSS

def init_layout() -> None:
    """
    Initialise la configuration globale de la page Streamlit 
    et injecte le design system CSS personnalisé.
    """
    st.set_page_config(
        page_title="ChemCook - Stoichiometry Hub",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # Injection du style CSS premium
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_header() -> None:
    """
    Affiche l'en-tête de l'application avec un titre à dégradé 
    et une description soignée pour le portfolio.
    """
    st.markdown("<h1>ChemCook 🧪</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -10px; margin-bottom: 25px; max-width: 800px;'>"
        "Un outil professionnel d'analyse stœchiométrique pour chimistes. "
        "Construisez une équation chimique, visualisez son tableau d'avancement interactif "
        "et simulez une mise à l'échelle (scale-up) en temps réel. "
        "Alimenté par un moteur de calcul chimique précis exposé via une API FastAPI."
        "</p>",
        unsafe_allow_html=True
    )

def render_footer() -> None:
    """
    Affiche le pied de page de l'application.
    """
    st.markdown("<br><br><hr style='border-color: rgba(255, 255, 255, 0.05);'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; color: #64748b; font-size: 0.85rem; padding: 10px 0;'>"
        "ChemCook &copy; 2026 • Projet Portfolio Scientifique & Technique • Construit avec FastAPI et Streamlit"
        "</div>",
        unsafe_allow_html=True
    )
