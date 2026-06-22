def quantity_to_moles(quantity: float | None, unit: str | None, mw: float | None,
                      density: float | None = None) -> float | None:
    """Converts quantity to moles from masses or volumes"""

    if quantity is None or unit is None:
        return None
    if unit == "mol":
        return quantity
    if unit == "mmol":
        return quantity / 1000
    if unit == "g" and mw:
        return quantity / mw
    if unit == "mg" and mw:
        return (quantity / 1000) / mw
    if unit == "mL" and density and mw:
        return (quantity * density) / mw
    return None


def find_limiting_reagent(species: list) -> tuple[int, float]:
    """Returns limiting reactant id and xmax for each reagent"""

    ratios = []
    for sp in species:
        if sp.role != "reactant":
            continue
        if sp.coeff <= 0:
            continue
        if sp.moles is None:
            continue
        ratios.append((sp.compound_id, sp.moles / sp.coeff)) #creating a 2 item tuple
    if not ratios: #empty list
        raise ValueError('No valid reactant or reactant quantities')
    return min(ratios, key=lambda x: x[1]) #sorts by lowest final advancement values

def build_avancement_table(species: list, xmax: float) -> list[dict]:
    "Create advancement table"

    rows = []
    for sp in species:
        n_0 = sp.moles or 0.0
        if sp.roles == "reactant":
            delta = -sp.coeff * xmax
        elif sp.roles == "product":
            delta = sp.coeff * xmax
        else:
            delta = 0.0
        rows.append({
            "species_name" : sp.compound.preferred_name,
            "role" : sp.role,
            "coeff" : sp.coeff,
            "n_init" : n_0,
            "n_final" : n_0 + delta,
            "delta_n" : delta
            })
    return rows
