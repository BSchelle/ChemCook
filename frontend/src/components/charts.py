import streamlit as st
import plotly.graph_objects as go
from typing import Any, Dict, List

def render_stoichiometric_chart(species_results: List[Dict[str, Any]], xmax: float) -> None:
    """
    Génère et affiche un graphique Plotly interactif illustrant les courbes
    d'évolution stœchiométrique des réactifs et des produits.
    """
    st.subheader("Profil d'Avancement Stœchiométrique")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -5px; margin-bottom: 15px;'>"
        "Ce graphique montre comment les quantités de matière (en moles) varient "
        "linéairement en fonction de l'avancement de la réaction (x), de l'état initial (x = 0) "
        "à l'état final (x = xmax)."
        "</p>",
        unsafe_allow_html=True
    )
    
    if not species_results or xmax is None or xmax <= 0:
        st.info("Saisissez des quantités positives de réactifs pour générer le profil d'avancement.")
        return

    # Palette de couleurs assortie au design system CSS
    role_colors = {
        "reactant": "#2dd4bf",   # Teal
        "product": "#f59e0b",    # Amber
        "solvent": "#a855f7",    # Purple
        "catalyst": "#ec4899",   # Pink
        "additive": "#64748b"    # Slate
    }
    
    fig = go.Figure()
    
    for sp in species_results:
        compound = sp.get("compound", {})
        name = compound.get("preferred_name", "N/A")
        role = sp.get("role", "reactant")
        n_init = sp.get("initial_moles")
        n_final = sp.get("final_moles")
        
        if n_init is None or n_final is None:
            continue
            
        color = role_colors.get(role, "#94a3b8")
        
        # Pour tracer une droite linéaire, l'état initial (x=0) et final (x=xmax) suffisent
        x_points = [0.0, xmax]
        y_points = [n_init, n_final]
        
        # Label lisible pour la légende
        role_label = {
            "reactant": "Réactif",
            "product": "Produit",
            "solvent": "Solvant",
            "catalyst": "Cat.",
            "additive": "Additif"
        }.get(role, role.capitalize())
        
        fig.add_trace(
            go.Scatter(
                x=x_points,
                y=y_points,
                mode="lines+markers",
                name=f"{name} ({role_label})",
                line=dict(color=color, width=3.5),
                marker=dict(size=8, symbol="circle"),
                hovertemplate=(
                    f"<b>{name}</b> ({role_label})<br>"
                    "Avancement (x) : %{x:.5g} mol<br>"
                    "Quantité (n) : %{y:.5g} mol<extra></extra>"
                )
            )
        )
        
    # Personnalisation de la mise en page (Layout) en mode sombre premium
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", # Transparent pour hériter du fond CSS de Streamlit
        plot_bgcolor="rgba(15, 23, 42, 0.3)",
        title=dict(
            text="Évolution des Quantités de Matière (n) vs Avancement (x)",
            font=dict(size=14, color="#f1f5f9", family="Outfit")
        ),
        xaxis=dict(
            title="Avancement de la réaction x (mol)",
            titlefont=dict(color="#94a3b8", size=11),
            tickfont=dict(color="#64748b"),
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            showline=True,
            linecolor="rgba(255,255,255,0.1)"
        ),
        yaxis=dict(
            title="Quantité de matière n (mol)",
            titlefont=dict(color="#94a3b8", size=11),
            tickfont=dict(color="#64748b"),
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            showline=True,
            linecolor="rgba(255,255,255,0.1)"
        ),
        legend=dict(
            font=dict(color="#cbd5e1", size=10),
            bgcolor="rgba(9, 11, 15, 0.8)",
            bordercolor="rgba(255,255,255,0.05)",
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="closest",
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)
