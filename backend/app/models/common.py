from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum
from datetime import datetime

class RoleEnum(str, Enum):
    """The role of a species in the reaction."""
    REACTANT = "reactant"
    PRODUCT = "product"
    SOLVENT = "solvent"
    CATALYST = "catalyst"
    ADDITIVE = "additive"

class UnitEnum(str, Enum):
    """Accepted units for quantities."""
    MASS_G = "mass_g"
    MASS_MG = "mass_mg"
    MASS_KG = "mass_kg"
    VOLUME_ML = "volume_ml"
    VOLUME_L = "volume_l"
    VOLUME_M3 = "volume_m3"
    MOLES = "moles"
    MILLIMOLES = "millimoles"

class QtyBase(BaseModel):
    "Base for a quantity w/ units"
    value: float = Field(..., gt=0)
    unit: UnitEnum = Field(...)
