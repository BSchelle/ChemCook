import streamlit as st
import traceback

from src.config import DEFAULT_API_URL
from src.api.client import ChemCookAPIClient
from src.components.layouts import init_layout, render_header, render_footer
from src.components.species_editor import render_species_editor, build_calculation_payload
from src.components.results_viewer import (
    render_metrics,
    render_species_results,
    render_advancement_table,
    render_scaled_quantities,
)
from src.components.charts import render_stoichiometric_chart



def main() -> None:
    # 1. Initialisation de la page et injection CSS
    init_layout()
    render_header()

    # 2. Configuration des paramètres dans la barre latérale (Sidebar)
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        api_url = st.text_input("Endpoint API Backend", value=DEFAULT_API_URL, help="URL de base de l'API FastAPI")
        reaction_id = st.number_input("ID Réaction", min_value=1, value=42, step=1, help="Identifiant numérique de la réaction")
        
        st.markdown("### ⚖️ Ajustements (Optionnels)")
        target_yield_percent = st.number_input(
            "Rendement Cible (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=0.0, 
            step=1.0, 
            help="Rendement attendu de la réaction. Utilisé pour calculer le facteur d'échelle à partir d'une masse produit cible."
        )
        scale_factor = st.number_input(
            "Facteur d'Échelle", 
            min_value=0.0, 
            value=0.0, 
            step=0.1, 
            help="Multiplicateur d'échelle global (ex: 2.0 pour doubler la réaction)."
        )
        target_mass_product_g = st.number_input(
            "Masse Produit Cible (g)", 
            min_value=0.0, 
            value=0.0, 
            step=0.1, 
            help="Masse théorique ou réelle ciblée pour le produit principal. Calcule automatiquement le facteur d'échelle."
        )
        
        st.markdown("---")
        st.markdown(
            "<div style='color: #64748b; font-size: 0.8rem;'>"
            "💡 Saisissez une masse produit cible ou un facteur d'échelle direct pour activer le module de mise à l'échelle (scale-up)."
            "</div>",
            unsafe_allow_html=True
        )

    # 3. Rendu de l'éditeur d'espèces stœchiométriques (Main)
    edited_rows = render_species_editor()

    # 4. Actions de calcul
    submit = st.button("Calculer la Stœchiométrie")
    
    if submit:
        # Validation basique côté client
        if len(edited_rows) < 2:
            st.error("⚠️ Erreur : Vous devez renseigner au moins deux espèces chimiques pour effectuer le calcul.")
            return
            
        # Construction du payload conforme à CalculationCreate
        payload = build_calculation_payload(
            reaction_id=int(reaction_id),
            target_yield_percent=target_yield_percent,
            scale_factor=scale_factor,
            target_mass_product_g=target_mass_product_g,
            rows=edited_rows
        )
        
        # Appel à l'API via le client
        client = ChemCookAPIClient(api_url)
        
        with st.spinner("Calcul stœchiométrique en cours..."):
            try:
                result = client.preview_calculation(payload)
                
                # Succès - Affichage des résultats
                st.toast("Calcul stœchiométrique réussi !", icon="✨")
                
                # Métriques générales
                render_metrics(result)
                
                # Visualisations côte à côte en deux onglets ou sections
                st.markdown("### 📊 Analyses & Modélisation", unsafe_allow_html=True)
                tab1, tab2 = st.tabs(["📈 Profil d'Avancement", "📋 Tableaux de Données"])
                
                with tab1:
                    # Graphique stœchiométrique Plotly
                    render_stoichiometric_chart(
                        result.get("species_results", []),
                        result.get("xmax", 0.0)
                    )
                
                with tab2:
                    # Tableau des espèces
                    render_species_results(result.get("species_results", []))
                    
                    # Tableau d'avancement
                    render_advancement_table(result.get("avancement_table", []))
                
                # Module de mise à l'échelle (si le scale-up a été activé)
                scaled_quantities = result.get("scaled_quantities")
                resolved_factor = result.get("scale_factor")
                if scaled_quantities and resolved_factor:
                    st.markdown("### 🚀 Module de Dimensionnement (Scale-up)", unsafe_allow_html=True)
                    render_scaled_quantities(scaled_quantities, resolved_factor)
                
            except ValueError as exc:
                # Erreur de validation métier renvoyée par le moteur chimique (ex: pas de réactif limitant, etc.)
                st.error(f"❌ Erreur Chimique : {exc}")
                st.markdown(
                    "<div style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>"
                    "Veuillez vérifier vos coefficients, rôles et quantités dans le tableau."
                    "</div>",
                    unsafe_allow_html=True
                )
            except ConnectionError as exc:
                # Erreur réseau : serveur éteint ou mauvaise URL
                st.error("🔌 Connexion Impossible")
                st.markdown(f"**Détail :** {exc}")
            except Exception as exc:
                # Erreurs inattendues
                st.error(f"💥 Une erreur inattendue est survenue : {exc}")
                with st.expander("Trace de débogage (Stacktrace)"):
                    st.code(traceback.format_exc())

    # 5. Rendu du pied de page
    render_footer()


if __name__ == "__main__":
    main()
