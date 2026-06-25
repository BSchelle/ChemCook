from datetime import datetime

import pytest

from backend.app.chemistry.engine import find_limiting_reagent, quantity_to_moles
from backend.app.models.calculation import CalculationCreate, CalculationRead
from backend.app.models.common import CompoundRefBase, QtyBase, RoleEnum, SpeciesQtyBase, UnitEnum
from backend.app.services.calculation_service import compute_reaction_calculation


def _compound(compound_id: int, name: str, mw: float | None, density: float | None = None) -> CompoundRefBase:
    return CompoundRefBase(
        compound_id=compound_id,
        preferred_name=name,
        molecular_weight=mw,
        density=density,
    )


def _species(
    compound_id: int,
    name: str,
    role: RoleEnum,
    coeff: float,
    qty: SpeciesQtyBase,
    mw: float | None,
    density: float | None = None,
):
    return {
        "compound": _compound(compound_id, name, mw, density),
        "role": role,
        "coeff": coeff,
        "qty": qty,
    }


def test_quantity_to_moles_from_mass():
    qty = SpeciesQtyBase(qty=QtyBase(value=10, unit=UnitEnum.MASS_G))

    assert quantity_to_moles(qty, mw=50) == pytest.approx(0.2)


def test_quantity_to_moles_from_volume_with_density():
    qty = SpeciesQtyBase(qty=QtyBase(value=10, unit=UnitEnum.VOLUME_ML), density=1000)

    assert quantity_to_moles(qty, mw=100, density=1000) == pytest.approx(0.1)


def test_quantity_to_moles_from_volume_without_density_raises():
    qty = SpeciesQtyBase(qty=QtyBase(value=10, unit=UnitEnum.VOLUME_ML))

    with pytest.raises(ValueError, match="Density is required"):
        quantity_to_moles(qty, mw=100, density=None)


def test_find_limiting_reagent_uses_initial_moles():
    species = [
        type(
            "Row",
            (),
            {
                "role": RoleEnum.REACTANT,
                "coeff": 2,
                "initial_moles": 0.6,
                "compound": _compound(1, "A", 50),
            },
        )(),
        type(
            "Row",
            (),
            {
                "role": RoleEnum.REACTANT,
                "coeff": 1,
                "initial_moles": 0.2,
                "compound": _compound(2, "B", 75),
            },
        )(),
    ]

    limiting_id, xmax = find_limiting_reagent(species)

    assert limiting_id == 2
    assert xmax == pytest.approx(0.2)


def test_compute_reaction_calculation_returns_complete_read_model():
    payload = CalculationCreate(
        reaction_id=42,
        species=[
            _species(
                1,
                "Reactant A",
                RoleEnum.REACTANT,
                1,
                SpeciesQtyBase(qty=QtyBase(value=10, unit=UnitEnum.MASS_G)),
                mw=50,
            ),
            _species(
                2,
                "Reactant B",
                RoleEnum.REACTANT,
                2,
                SpeciesQtyBase(qty=QtyBase(value=50, unit=UnitEnum.MILLIMOLES)),
                mw=80,
            ),
            _species(
                3,
                "Product C",
                RoleEnum.PRODUCT,
                1,
                SpeciesQtyBase(qty=QtyBase(value=5, unit=UnitEnum.MASS_G)),
                mw=150,
            ),
        ],
        scale_factor=2.0,
    )

    result = compute_reaction_calculation(payload)

    assert isinstance(result, CalculationRead)
    assert result.reaction_id == 42
    assert result.limiting_reactant_id == 2
    assert result.limiting_reactant_name == "Reactant B"
    assert result.xmax == pytest.approx(0.025)
    assert result.theoretical_yield_moles == pytest.approx(0.025)
    assert result.theoretical_yield_mass_g == pytest.approx(3.75)
    assert len(result.species_results) == 3
    assert len(result.avancement_table) == 3
    assert result.species_results[1].limiting_reactant is True
    assert result.species_results[0].final_moles == pytest.approx(0.175)
    assert result.species_results[2].theoretical_yield_mass == pytest.approx(3.75)
    assert result.scaled_quantities is not None
    assert result.scaled_quantities[0].initial_moles == pytest.approx(result.species_results[0].initial_moles * 2)
    assert isinstance(result.created_at, datetime)
