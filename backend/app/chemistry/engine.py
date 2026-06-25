from __future__ import annotations

from typing import Protocol, Sequence

from backend.app.chemistry.converter import quantity_to_moles
from backend.app.models.calculation import AvancementRow
from backend.app.models.common import CompoundRefBase, RoleEnum, SpeciesQtyBase


class _CalculationSpeciesRow(Protocol):
    role: RoleEnum
    coeff: float
    initial_moles: float | None
    compound: CompoundRefBase


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
