import streamlit as st
from typing import Any, Dict, List

def _get_role_badge(role: str) -> str:
    """
    Retourne un badge HTML stylisé selon le rôle de l'espèce.
    """
    role_translations = {
        "reactant": "Réactif",
        "product": "Produit",
        "solvent": "Solvant",
        "catalyst": "Catalyseur",
        "additive": "Additif"
    }
    label = role_translations.get(role, role.capitalize())
    return f'<span class="role-badge role-{role}">{label}</span>'

def render_metrics(result: Dict[str, Any]) -> None:
    """
    Affiche la grille de métriques stœchiométriques clés sous forme de cartes.
    """
    st.subheader("Synthèse Stœchiométrique")
    col1, col2, col3, col4 = st.columns(4)
    
    limiting_name = result.get("limiting_reactant_name") or "N/A"
    xmax = result.get("xmax")
    theo_mass = result.get("theoretical_yield_mass_g")
    theo_moles = result.get("theoretical_yield_moles")
    
    col1.metric("Réactif Limitant", limiting_name)
    col2.metric("Avancement Max (xmax)", f"{xmax:.5g}" if xmax is not None else "N/A")
    col3.metric("Masse Théorique", f"{theo_mass:.5g} g" if theo_mass is not None else "N/A")
    col4.metric("Moles Théoriques", f"{theo_moles:.5g} mol" if theo_moles is not None else "N/A")

def _render_html_table(headers: List[str], rows: List[List[Any]]) -> None:
    """
    Génère et affiche un tableau HTML propre avec style CSS sombre et bordures subtiles.
    """
    html = """
    <table style="width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.9rem; text-align: left; background-color: rgba(17, 24, 39, 0.4); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
        <thead>
            <tr style="background-color: rgba(30, 41, 59, 0.8); border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
    """
    for header in headers:
        html += f'<th style="padding: 12px 16px; font-weight: 600; color: #94a3b8;">{header}</th>'
    html += "</tr></thead><tbody>"
    
    for i, row in enumerate(rows):
        bg_color = "rgba(15, 23, 42, 0.2)" if i % 2 == 0 else "rgba(15, 23, 42, 0.4)"
        html += f'<tr style="background-color: {bg_color}; border-bottom: 1px solid rgba(255, 255, 255, 0.03);">'
        for cell in row:
            html += f'<td style="padding: 12px 16px; color: #cbd5e1; vertical-align: middle;">{cell}</td>'
        html += "</tr>"
        
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

def render_species_results(species_results: List[Dict[str, Any]]) -> None:
    """
    Affiche le tableau détaillé des résultats par espèce avec des badges de rôle HTML.
    """
    st.subheader("Résultats par Espèce")
    headers = [
        "Espèce", "Rôle", "Coeff.", "Limitant ?", 
        "Moles Initiales", "Moles Finales", "Masse Requise", "Volume Requis"
    ]
    
    rows = []
    for sp in species_results:
        compound = sp.get("compound", {})
        name = compound.get("preferred_name", "N/A")
        role = sp.get("role", "reactant")
        coeff = sp.get("coeff", 1.0)
        is_limiting = "⭐ Oui" if sp.get("limiting_reactant") else "Non"
        
        n_init = sp.get("initial_moles")
        n_final = sp.get("final_moles")
        mass_req = sp.get("required_mass_g")
        vol_req = sp.get("required_volume_mL")
        
        row = [
            f"<b>{name}</b>",
            _get_role_badge(role),
            f"{coeff:.4g}",
            is_limiting,
            f"{n_init:.5g} mol" if n_init is not None else "N/A",
            f"{n_final:.5g} mol" if n_final is not None else "N/A",
            f"{mass_req:.4g} g" if mass_req is not None else "N/A",
            f"{vol_req:.4g} mL" if vol_req is not None else "N/A"
        ]
        rows.append(row)
        
    _render_html_table(headers, rows)

def render_advancement_table(avancement_rows: List[Dict[str, Any]]) -> None:
    """
    Affiche le tableau d'avancement de la réaction.
    """
    st.subheader("Tableau d'Avancement Réactif/Produit")
    headers = [
        "Espèce", "Rôle", "Coeff.", 
        "Quantité Initiale (t=0)", "Variation (Δn)", "Quantité Finale (t_final)"
    ]
    
    rows = []
    for row_data in avancement_rows:
        name = row_data.get("species_name", "N/A")
        role = row_data.get("role", "reactant")
        coeff = row_data.get("coeff", 1.0)
        n_init = row_data.get("n_init", 0.0)
        n_final = row_data.get("n_final")
        delta_n = row_data.get("delta_n")
        
        # Formatage de la variation stœchiométrique
        sign = "+" if role == "product" else "-"
        delta_str = f"{sign} {coeff:.4g} &times; xmax" if role in ("reactant", "product") else "0 (Solvant/Cat.)"
        if delta_n is not None:
            delta_str += f" ({delta_n:+.4g} mol)"
            
        row = [
            f"<b>{name}</b>",
            _get_role_badge(role),
            f"{coeff:.4g}",
            f"{n_init:.5g} mol",
            delta_str,
            f"<b>{n_final:.5g} mol</b>" if n_final is not None else "N/A"
        ]
        rows.append(row)
        
    _render_html_table(headers, rows)

def render_scaled_quantities(scaled_species: List[Dict[str, Any]], scale_factor: float) -> None:
    """
    Affiche le tableau des quantités après mise à l'échelle (scale-up).
    """
    st.subheader(f"Quantités Recalculées (Facteur d'échelle : {scale_factor:.4g})")
    st.markdown(
        "<p style='color: #2dd4bf; font-size: 0.9rem; margin-top: -5px; margin-bottom: 15px;'>"
        "Les quantités ci-dessous correspondent au dimensionnement ajusté pour atteindre votre objectif de production."
        "</p>",
        unsafe_allow_html=True
    )
    
    headers = [
        "Espèce", "Rôle", "Moles Recalculées", 
        "Masse Requise (Scalée)", "Volume Requis (Scalé)"
    ]
    
    rows = []
    for sp in scaled_species:
        compound = sp.get("compound", {})
        name = compound.get("preferred_name", "N/A")
        role = sp.get("role", "reactant")
        
        n_init = sp.get("initial_moles")
        mass_req = sp.get("required_mass_g")
        vol_req = sp.get("required_volume_mL")
        
        row = [
            f"<b>{name}</b>",
            _get_role_badge(role),
            f"{n_init:.5g} mol" if n_init is not None else "N/A",
            f'<span style="color: #2dd4bf; font-weight: 600;">{mass_req:.4g} g</span>' if mass_req is not None else "N/A",
            f'<span style="color: #38bdf8; font-weight: 600;">{vol_req:.4g} mL</span>' if vol_req is not None else "N/A"
        ]
        rows.append(row)
        
    _render_html_table(headers, rows)
