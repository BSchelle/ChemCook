from __future__ import annotations

from typing import Protocol, Sequence

from backend.app.models.calculation import AvancementRow
from backend.app.models.common import CompoundRefBase, RoleEnum, SpeciesQtyBase, UnitEnum


class _CalculationSpeciesRow(Protocol):
    role: RoleEnum
    coeff: float
    initial_moles: float | None
    compound: CompoundRefBase


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
    elif unit in (UnitEnum.MASS_G, UnitEnum.MASS_MG, UnitEnum.MASS_KG, UnitEnum.MOLES, UnitEnum.MILLIMOLES):
        if unit in (UnitEnum.MASS_G, UnitEnum.MASS_MG, UnitEnum.MASS_KG) and mw is None:
            raise ValueError("Molecular weight is required to convert masses to moles")

    if unit == UnitEnum.MASS_G and mw is not None:
        return value / mw
    if unit == UnitEnum.MASS_MG and mw is not None:
        return (value / 1000) / mw
    if unit == UnitEnum.MASS_KG and mw is not None:
        return (value * 1000) / mw
    if unit == UnitEnum.VOLUME_ML and density is not None and mw is not None:
        return (value * density) / (mw * 1000)
    if unit == UnitEnum.VOLUME_L and density is not None and mw is not None:
        return (value * density) / mw
    if unit == UnitEnum.VOLUME_M3 and density is not None and mw is not None:
        return (value * 1000 * density) / mw
    if unit == UnitEnum.MOLES:
        return value
    if unit == UnitEnum.MILLIMOLES:
        return value / 1000

    raise ValueError(f"Unsupported quantity unit: {unit}")


def find_limiting_reagent(species: Sequence[_CalculationSpeciesRow]) -> tuple[int, float]:
    """Returns (compound_id, xmax) for limiting reagent."""

    ratios: list[tuple[int, float]] = []
    for sp in species:
        if sp.role != RoleEnum.REACTANT:
            continue
        if sp.coeff <= 0:
            continue
        if sp.initial_moles is None:
            continue
        ratios.append((sp.compound.compound_id, sp.initial_moles / sp.coeff))

    if not ratios:
        raise ValueError("No valid reactant quantities")
    return min(ratios, key=lambda x: x[1])


def build_avancement_table(species: Sequence[_CalculationSpeciesRow], xmax: float) -> list[AvancementRow]:
    """Create advancement table."""

    rows = []
    for sp in species:
        n_0 = sp.initial_moles or 0.0
        if sp.role == RoleEnum.REACTANT:
            delta = -sp.coeff * xmax
        elif sp.role == RoleEnum.PRODUCT:
            delta = sp.coeff * xmax
        else:
            delta = 0.0
        n_final = max(0.0, n_0 + delta)
        rows.append(
            AvancementRow(
                species_name=sp.compound.preferred_name,
                role=sp.role,
                coeff=sp.coeff,
                n_init=n_0,
                n_final=n_final,
                delta_n=delta,
            )
        )
    return rows
