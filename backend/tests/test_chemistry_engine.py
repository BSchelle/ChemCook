from types import SimpleNamespace

import pytest

from backend.app.chemistry.engine import build_avancement_table, find_limiting_reagent, quantity_to_moles
from backend.app.models.calculation import AvancementRow
from backend.app.models.common import CompoundRefBase, QtyBase, RoleEnum, SpeciesQtyBase, UnitEnum


def _compound(compound_id: int, name: str, mw: float | None, density: float | None = None) -> CompoundRefBase:
    return CompoundRefBase(
        compound_id=compound_id,
        preferred_name=name,
        molecular_weight=mw,
        density=density,
    )


def _qty(value: float, unit: UnitEnum, density: float | None = None) -> SpeciesQtyBase:
    return SpeciesQtyBase(qty=QtyBase(value=value, unit=unit), density=density)


def _row(
    compound_id: int,
    name: str,
    role: RoleEnum,
    coeff: float,
    initial_moles: float | None,
    mw: float | None,
    density: float | None = None,
):
    return SimpleNamespace(
        compound=_compound(compound_id, name, mw, density),
        role=role,
        coeff=coeff,
        initial_moles=initial_moles,
    )


def test_quantity_to_moles_from_mass():
    qty = _qty(10, UnitEnum.MASS_G)

    assert quantity_to_moles(qty, mw=50) == pytest.approx(0.2)


def test_quantity_to_moles_from_volume_with_density():
    qty = _qty(10, UnitEnum.VOLUME_ML)

    assert quantity_to_moles(qty, mw=100, density=1000) == pytest.approx(0.1)


def test_quantity_to_moles_from_volume_without_density_raises():
    qty = _qty(10, UnitEnum.VOLUME_ML)

    with pytest.raises(ValueError, match="Density is required to convert volumes to moles"):
        quantity_to_moles(qty, mw=100, density=None)


def test_quantity_to_moles_accepts_direct_moles():
    qty = SpeciesQtyBase(moles=0.75)

    assert quantity_to_moles(qty, mw=None) == pytest.approx(0.75)


def test_find_limiting_reagent_picks_lowest_ratio():
    species = [
        _row(1, "A", RoleEnum.REACTANT, 2, 0.6, 50),
        _row(2, "B", RoleEnum.REACTANT, 1, 0.2, 75),
        _row(3, "C", RoleEnum.PRODUCT, 1, 1.0, 100),
    ]

    limiting_id, xmax = find_limiting_reagent(species)

    assert limiting_id == 2
    assert xmax == pytest.approx(0.2)


def test_find_limiting_reagent_raises_without_reactant_quantity():
    species = [
        _row(1, "A", RoleEnum.REACTANT, 2, None, 50),
        _row(2, "B", RoleEnum.PRODUCT, 1, 0.2, 75),
    ]

    with pytest.raises(ValueError, match="No valid reactant quantities"):
        find_limiting_reagent(species)


def test_build_avancement_table_uses_roles_and_initial_moles():
    species = [
        _row(1, "A", RoleEnum.REACTANT, 2, 0.6, 50),
        _row(2, "B", RoleEnum.PRODUCT, 1, 0.2, 75),
        _row(3, "Solvent", RoleEnum.SOLVENT, 1, None, None),
    ]

    rows = build_avancement_table(species, xmax=0.2)

    assert len(rows) == 3
    assert rows[0].species_name == "A"
    assert rows[0].role == RoleEnum.REACTANT
    assert rows[0].coeff == 2
    assert rows[0].n_init == pytest.approx(0.6)
    assert rows[0].n_final == pytest.approx(0.2)
    assert rows[0].delta_n == pytest.approx(-0.4)
    assert rows[1].species_name == "B"
    assert rows[1].role == RoleEnum.PRODUCT
    assert rows[1].coeff == 1
    assert rows[1].n_init == pytest.approx(0.2)
    assert rows[1].n_final == pytest.approx(0.4)
    assert rows[1].delta_n == pytest.approx(0.2)
    assert rows[2].species_name == "Solvent"
    assert rows[2].role == RoleEnum.SOLVENT
    assert rows[2].coeff == 1
    assert rows[2].n_init == pytest.approx(0.0)
    assert rows[2].n_final == pytest.approx(0.0)
    assert rows[2].delta_n == pytest.approx(0.0)
