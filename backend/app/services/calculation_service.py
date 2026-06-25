from __future__ import annotations

from datetime import datetime, timezone

from backend.app.chemistry.engine import build_avancement_table, find_limiting_reagent, quantity_to_moles
from backend.app.models.calculation import CalculationCreate, CalculationRead, ReactionSpeciesResult, ReactionSpeciesForCalculationBase
from backend.app.models.common import RoleEnum, SpeciesQtyBase, UnitEnum


def _effective_density(species: ReactionSpeciesForCalculationBase) -> float | None:
    return species.qty.density if species.qty and species.qty.density is not None else species.compound.density


def _quantity_to_mass_and_volume(
    qty: SpeciesQtyBase | None,
    mw: float | None,
    density: float | None,
) -> tuple[float | None, float | None]:
    if qty is None:
        return None, None

    if qty.moles is not None:
        if mw is None:
            raise ValueError("Molecular weight is required to convert moles to mass")
        mass_g = qty.moles * mw
        volume_mL = mass_g * 1000 / density if density is not None else None
        return mass_g, volume_mL

    if qty.millimoles is not None:
        if mw is None:
            raise ValueError("Molecular weight is required to convert millimoles to mass")
        mass_g = (qty.millimoles / 1000) * mw
        volume_mL = mass_g * 1000 / density if density is not None else None
        return mass_g, volume_mL

    if qty.qty is None:
        return None, None

    value = qty.qty.value
    unit = qty.qty.unit

    mass_g: float | None = None
    volume_mL: float | None = None

    if unit == UnitEnum.MASS_G:
        mass_g = value
    elif unit == UnitEnum.MASS_MG:
        mass_g = value / 1000
    elif unit == UnitEnum.MASS_KG:
        mass_g = value * 1000
    elif unit == UnitEnum.VOLUME_ML:
        volume_mL = value
    elif unit == UnitEnum.VOLUME_L:
        volume_mL = value * 1000
    elif unit == UnitEnum.VOLUME_M3:
        volume_mL = value * 1_000_000
    elif unit == UnitEnum.MOLES:
        if mw is None:
            raise ValueError("Molecular weight is required to convert moles to mass")
        mass_g = value * mw
    elif unit == UnitEnum.MILLIMOLES:
        if mw is None:
            raise ValueError("Molecular weight is required to convert millimoles to mass")
        mass_g = (value / 1000) * mw
    else:
        raise ValueError(f"Unsupported quantity unit: {unit}")

    if mass_g is None and volume_mL is not None and density is not None:
        mass_g = density * volume_mL / 1000
    if volume_mL is None and mass_g is not None and density is not None:
        volume_mL = mass_g * 1000 / density

    return mass_g, volume_mL


def _scale_species_result(species: ReactionSpeciesResult, factor: float) -> ReactionSpeciesResult:
    return species.model_copy(
        update={
            "initial_moles": species.initial_moles * factor if species.initial_moles is not None else None,
            "final_moles": species.final_moles * factor if species.final_moles is not None else None,
            "theoretical_yield_moles": (
                species.theoretical_yield_moles * factor if species.theoretical_yield_moles is not None else None
            ),
            "theoretical_yield_mass": (
                species.theoretical_yield_mass * factor if species.theoretical_yield_mass is not None else None
            ),
            "required_mass_g": species.required_mass_g * factor if species.required_mass_g is not None else None,
            "required_volume_mL": species.required_volume_mL * factor if species.required_volume_mL is not None else None,
        }
    )


def _resolve_scale_factor(payload: CalculationCreate, theoretical_yield_mass_g: float) -> float | None:
    if payload.scale_factor is not None:
        return payload.scale_factor

    if payload.target_mass_product_g is None:
        return None

    if payload.target_yield_percent is not None:
        if payload.target_yield_percent <= 0:
            raise ValueError("Target yield percent must be greater than zero to scale from a target product mass")
        target_mass_theoretical = payload.target_mass_product_g / (payload.target_yield_percent / 100)
    else:
        target_mass_theoretical = payload.target_mass_product_g

    if theoretical_yield_mass_g <= 0:
        raise ValueError("Theoretical yield mass must be positive to compute a scale factor")

    return target_mass_theoretical / theoretical_yield_mass_g


def compute_reaction_calculation(payload: CalculationCreate) -> CalculationRead:
    species_results: list[ReactionSpeciesResult] = []

    for species in payload.species:
        effective_density = _effective_density(species)
        initial_moles = quantity_to_moles(
            species.qty,
            species.compound.molecular_weight,
            effective_density,
        )
        if initial_moles is None:
            raise ValueError(f"Unable to convert quantity for species {species.compound.preferred_name}")

        required_mass_g, required_volume_mL = _quantity_to_mass_and_volume(
            species.qty,
            species.compound.molecular_weight,
            effective_density,
        )

        species_results.append(
            ReactionSpeciesResult(
                compound=species.compound,
                role=species.role,
                coeff=species.coeff,
                qty=species.qty,
                limiting_reactant=False,
                initial_moles=initial_moles,
                final_moles=None,
                theoretical_yield_moles=None,
                theoretical_yield_mass=None,
                required_mass_g=required_mass_g,
                required_volume_mL=required_volume_mL,
            )
        )

    limiting_reactant_id, xmax = find_limiting_reagent(species_results)

    for species in species_results:
        initial_moles = species.initial_moles
        if initial_moles is None:
            raise ValueError(f"Missing initial moles for {species.compound.preferred_name}")

        if species.role == RoleEnum.REACTANT:
            species.final_moles = max(0.0, initial_moles - (species.coeff * xmax))
        elif species.role == RoleEnum.PRODUCT:
            species.final_moles = initial_moles + (species.coeff * xmax)
        else:
            species.final_moles = initial_moles

        species.limiting_reactant = species.compound.compound_id == limiting_reactant_id

    product_rows = [species for species in species_results if species.role == RoleEnum.PRODUCT]
    if len(product_rows) != 1:
        raise ValueError("Global yield is ambiguous without exactly one product species")

    product = product_rows[0]
    if product.compound.molecular_weight is None:
        raise ValueError("Molecular weight is required to compute the theoretical product yield")

    theoretical_yield_moles = product.coeff * xmax
    theoretical_yield_mass_g = theoretical_yield_moles * product.compound.molecular_weight
    product.theoretical_yield_moles = theoretical_yield_moles
    product.theoretical_yield_mass = theoretical_yield_mass_g

    avancement_table = build_avancement_table(species_results, xmax)

    scaled_quantities = None
    scale_factor = _resolve_scale_factor(payload, theoretical_yield_mass_g)
    if scale_factor is not None:
        scaled_quantities = [_scale_species_result(species, scale_factor) for species in species_results]

    return CalculationRead(
        id=payload.reaction_id,
        reaction_id=payload.reaction_id,
        species=[species.model_copy(deep=True) for species in payload.species],
        target_yield_percent=payload.target_yield_percent,
        scale_factor=payload.scale_factor,
        target_mass_product_g=payload.target_mass_product_g,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
        limiting_reactant_id=limiting_reactant_id,
        limiting_reactant_name=next(
            species.compound.preferred_name for species in species_results if species.compound.compound_id == limiting_reactant_id
        ),
        xmax=xmax,
        theoretical_yield_moles=theoretical_yield_moles,
        theoretical_yield_mass_g=theoretical_yield_mass_g,
        species_results=species_results,
        avancement_table=avancement_table,
        scaled_quantities=scaled_quantities,
    )
