from typing import Sequence
from backend.app.models.common import RoleEnum, SpeciesQtyBase, UnitEnum
from backend.app.models.reaction  import ReactionSpeciesRead


def quantity_to_moles(
    qty: SpeciesQtyBase | None,
    mw: float | None,
    density: float | None = None,
) -> float | None:
    """Converts quantity to moles from masses or volumes"""

    if qty is None:
        return None

    if qty.moles is not None:
        return qty.moles

    if qty.millimoles is not None:
        return qty.millimoles / 1000

    if qty.qty is None:
        return None

    value = qty.qty.value
    unit = qty.qty.unit

    if unit in (UnitEnum.VOLUME_L, UnitEnum.VOLUME_ML, UnitEnum.VOLUME_M3):
        if density is None:
            raise ValueError("Density is required to convert volumes to moles")
        if mw is None:
            raise ValueError("Molecular weight is required to convert volumes to moles")

    if unit == UnitEnum.MASS_G and mw:
        return value / mw
    if unit == UnitEnum.MASS_MG and mw:
        return (value / 1000) / mw
    if unit == UnitEnum.VOLUME_ML and density and mw:
        return (value * density) / mw
    if unit == UnitEnum.VOLUME_L and density and mw:
        return (value * 1000 * density) / mw

    return None

def find_limiting_reagent(species: Sequence[ReactionSpeciesRead],) -> tuple[int, float]:
    """Returns (compound_id, xmax) for limiting reagent"""

    ratios: list[tuple[int, float]] = []
    for sp in species:
        if sp.role != RoleEnum.REACTANT:
            continue
        if sp.coeff <= 0:
            continue
        if sp.calculated_moles is None:
            continue
        ratios.append((sp.id, sp.calculated_moles / sp.coeff)) #creating a 2 item tuple

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
