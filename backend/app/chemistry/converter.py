from __future__ import annotations

from backend.app.models.common import SpeciesQtyBase, UnitEnum


def quantity_to_moles(
    qty: SpeciesQtyBase | None,
    mw: float | None,
    density: float | None = None,
) -> float | None:
    """
    Converts quantity to moles from masses or volumes.
    
    Density is expected in kg/m3 (SI norm).
    Molecular weight (mw) is expected in g/mol.
    """
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

    # Validate required data before conversions
    if unit in (UnitEnum.VOLUME_L, UnitEnum.VOLUME_ML, UnitEnum.VOLUME_M3):
        if density is None:
            raise ValueError("Density is required to convert volumes to moles")
        if mw is None:
            raise ValueError("Molecular weight is required to convert volumes to moles")
    elif unit in (UnitEnum.MASS_G, UnitEnum.MASS_MG, UnitEnum.MASS_KG):
        if mw is None:
            raise ValueError("Molecular weight is required to convert masses to moles")

    # Conversion calculations
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


def quantity_to_mass_and_volume(
    qty: SpeciesQtyBase | None,
    mw: float | None,
    density: float | None = None,
) -> tuple[float | None, float | None]:
    """
    Converts any quantity representation to its equivalent mass (g) 
    and volume (mL).
    
    Density is expected in kg/m3 (SI norm).
    Molecular weight (mw) is expected in g/mol.
    """
    if qty is None:
        return None, None

    # Moles direct input
    if qty.moles is not None:
        if mw is None:
            raise ValueError("Molecular weight is required to convert moles to mass")
        mass_g = qty.moles * mw
        volume_mL = mass_g * 1000 / density if density is not None else None
        return mass_g, volume_mL

    # Millimoles direct input
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

    # Raw conversion based on unit
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

    # Cross calculations mass <-> volume if density is provided
    if mass_g is None and volume_mL is not None and density is not None:
        mass_g = density * volume_mL / 1000
    if volume_mL is None and mass_g is not None and density is not None:
        volume_mL = mass_g * 1000 / density

    return mass_g, volume_mL
