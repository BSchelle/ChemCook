def quantity_to_moles(quantity: float | None, unit: str | None, mw: float | None,
                      density: float | None = None) -> float | None:
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
