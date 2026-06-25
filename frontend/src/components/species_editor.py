import streamlit as st
from typing import Any, Dict, List

def empty_species_row(index: int) -> Dict[str, Any]:
    """
    Génère une ligne d'espèce simplifiée, claire et intuitive pour l'éditeur.
    """
    return {
        "preferred_name": f"Espèce {index + 1}",
        "role": "reactant" if index < 2 else "solvent",
        "eq": 1.0,
        "quantity_value": 1.0,
        "quantity_unit": "mass_g",
        "molecular_weight": 100.0,
        "density": None,
    }

def render_species_editor() -> List[Dict[str, Any]]:
    """
    Affiche le tableau d'édition simplifié contenant exactement les colonnes
    demandées pour une lisibilité maximale (qualité portfolio).
    """
    st.subheader("Composition de la Réaction")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -5px; margin-bottom: 15px;'>"
        "Saisissez vos réactifs, produits et solvants. Renseignez leurs quantités, "
        "leurs masses molaires, leurs densités (si volume) et leurs équivalents stœchiométriques (eq)."
        "</p>",
        unsafe_allow_html=True
    )

    # Initialisation de l'état si vide
    if "species_rows" not in st.session_state:
        st.session_state.species_rows = [empty_species_row(0), empty_species_row(1)]

    edited_rows = st.data_editor(
        st.session_state.species_rows,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "preferred_name": st.column_config.TextColumn("Nom de l'espèce", required=True, help="Nom ou formule chimique de la molécule"),
            "role": st.column_config.SelectboxColumn(
                "Rôle", 
                options=["reactant", "product", "solvent", "catalyst", "additive"],
                required=True,
                help="Rôle de l'espèce dans le processus chimique"
            ),
            "eq": st.column_config.NumberColumn("eq", min_value=0.0001, format="%.4f", step=0.5, help="Équivalents stœchiométriques (remplace le coefficient)"),
            "quantity_value": st.column_config.NumberColumn("Quantité (valeur)", min_value=0.0001, format="%.4f", step=1.0, help="Valeur de la quantité engagée"),
            "quantity_unit": st.column_config.SelectboxColumn(
                "Unité",
                options=["mass_g", "mass_mg", "mass_kg", "volume_ml", "volume_l", "moles", "millimoles"],
                required=True,
                help="Unité de mesure (masse, volume ou quantité de matière)"
            ),
            "molecular_weight": st.column_config.NumberColumn("Masse Molaire (g/mol)", min_value=0.0001, format="%.2f", step=1.0, help="Masse molaire (requise pour convertir la masse/volume en moles)"),
            "density": st.column_config.NumberColumn("Densité (g/mL)", min_value=0.0001, format="%.3f", step=0.1, help="Densité de l'espèce (requise pour convertir les volumes en moles)"),
        },
    )
    
    st.session_state.species_rows = edited_rows
    return edited_rows

def build_calculation_payload(
    reaction_id: int, 
    target_yield_percent: float, 
    scale_factor: float, 
    target_mass_product_g: float, 
    rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Transforme les lignes simplifiées de l'éditeur en payload JSON structuré 
    attendu par le schéma Pydantic du backend, en effectuant les correspondances nécessaires.
    """
    species = []
    for index, row in enumerate(rows):
        qty: Dict[str, Any] = {}
        unit = row["quantity_unit"]
        value = float(row["quantity_value"])
        
        # Gestion unifiée des unités (moles directes ou grandeurs physiques)
        if unit == "moles":
            qty["moles"] = value
            qty["qty"] = None
        elif unit == "millimoles":
            qty["millimoles"] = value
            qty["qty"] = None
        else:
            qty["qty"] = {
                "value": value,
                "unit": unit,
            }
            qty["moles"] = None
            qty["millimoles"] = None

        # Densité unique
        density = row.get("density")
        if density not in (None, ""):
            qty["density"] = float(density)

        species.append(
            {
                "compound": {
                    "compound_id": index + 1,  # Identifiant généré automatiquement
                    "preferred_name": str(row["preferred_name"]),
                    "molecular_weight": float(row["molecular_weight"]) if row.get("molecular_weight") not in (None, "") else None,
                    "density": float(density) if density not in (None, "") else None,
                },
                "role": row["role"],
                "coeff": float(row["eq"]),  # Les équivalents (eq) sont mappés sur le coefficient stœchiométrique
                "qty": qty,
            }
        )

    payload = {
        "reaction_id": reaction_id,
        "species": species,
    }
    
    if target_yield_percent > 0:
        payload["target_yield_percent"] = float(target_yield_percent)
    if scale_factor > 0:
        payload["scale_factor"] = float(scale_factor)
    if target_mass_product_g > 0:
        payload["target_mass_product_g"] = float(target_mass_product_g)
        
    return payload
