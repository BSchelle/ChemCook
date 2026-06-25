import streamlit as st
from typing import Any, Dict, List

def empty_species_row(index: int) -> Dict[str, Any]:
    """
    Génère une ligne vide par défaut pour l'éditeur d'espèces.
    """
    return {
        "compound_id": index + 1,
        "preferred_name": f"Espèce {index + 1}",
        "role": "reactant",
        "coeff": 1.0,
        "quantity_value": 1.0,
        "quantity_unit": "mass_g",
        "molecular_weight": 50.0,
        "compound_density": None,
        "species_density": None,
        "moles": None,
        "millimoles": None,
    }

def render_species_editor() -> List[Dict[str, Any]]:
    """
    Affiche le tableau d'édition interactif pour saisir les espèces chimiques.
    Retourne la liste des lignes saisies par l'utilisateur.
    """
    st.subheader("Composition de la Réaction")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -5px; margin-bottom: 15px;'>"
        "Saisissez au moins 2 espèces chimiques (réactifs, produits, solvants, etc.) "
        "avec leurs coefficients stœchiométriques et quantités."
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
            "compound_id": st.column_config.NumberColumn("ID Composé", min_value=1, step=1, help="Identifiant unique du composé"),
            "preferred_name": st.column_config.TextColumn("Nom de l'espèce", required=True),
            "role": st.column_config.SelectboxColumn(
                "Rôle", 
                options=["reactant", "product", "solvent", "catalyst", "additive"],
                required=True,
                help="Rôle de l'espèce dans le processus chimique"
            ),
            "coeff": st.column_config.NumberColumn("Coeff", min_value=0.0001, format="%.4f", step=0.5, help="Coefficient stœchiométrique (ex: 1, 2, 0.5)"),
            "quantity_value": st.column_config.NumberColumn("Valeur Qté", min_value=0.0001, format="%.4f", step=1.0, help="Valeur numérique de la quantité engagée"),
            "quantity_unit": st.column_config.SelectboxColumn(
                "Unité Qté",
                options=["mass_g", "mass_mg", "mass_kg", "volume_ml", "volume_l", "volume_m3", "moles", "millimoles"],
                required=True,
                help="Unité de mesure associée à la valeur de la quantité"
            ),
            "molecular_weight": st.column_config.NumberColumn("Masse Molaire (g/mol)", min_value=0.0001, format="%.2f", step=1.0, help="Masse molaire requise pour convertir en moles"),
            "compound_density": st.column_config.NumberColumn("Densité Composé (g/mL)", min_value=0.0001, format="%.3f", step=0.1, help="Densité par défaut du composé pur"),
            "species_density": st.column_config.NumberColumn("Densité Espèce (g/mL)", min_value=0.0001, format="%.3f", step=0.1, help="Densité spécifique de la solution"),
            "moles": st.column_config.NumberColumn("Moles directes", min_value=0.0001, format="%.6f", step=0.1, help="Saisie directe en moles (écrase la quantité)"),
            "millimoles": st.column_config.NumberColumn("mmol directes", min_value=0.0001, format="%.3f", step=0.1, help="Saisie directe en millimoles (écrase la quantité)"),
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
    Transforme les lignes brutes de l'éditeur en payload JSON structuré 
    attendu par le schéma Pydantic CalculationCreate du backend.
    """
    species = []
    for row in rows:
        qty: Dict[str, Any] = {}
        if row.get("moles") not in (None, ""):
            qty["moles"] = float(row["moles"])
        if row.get("millimoles") not in (None, ""):
            qty["millimoles"] = float(row["millimoles"])
            
        # Si pas de saisie directe en moles, on prend la quantité valeur/unité
        if "moles" not in qty and "millimoles" not in qty:
            qty["qty"] = {
                "value": float(row["quantity_value"]),
                "unit": row["quantity_unit"],
            }
        else:
            qty["qty"] = None

        # La densité effective correspond à la densité spécifique ou celle du composé
        density = row.get("species_density") if row.get("species_density") not in (None, "") else row.get("compound_density")
        if density not in (None, ""):
            qty["density"] = float(density)

        species.append(
            {
                "compound": {
                    "compound_id": int(row["compound_id"]),
                    "preferred_name": str(row["preferred_name"]),
                    "molecular_weight": float(row["molecular_weight"]) if row.get("molecular_weight") not in (None, "") else None,
                    "density": float(row["compound_density"]) if row.get("compound_density") not in (None, "") else None,
                },
                "role": row["role"],
                "coeff": float(row["coeff"]),
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
