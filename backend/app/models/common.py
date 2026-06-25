from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum
from datetime import datetime

# 1 - Shared enumerated types

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

class PhaseEnum(str, Enum):
    """Physical phase"""
    GAS = "gas"
    LIQUID = "liquid"
    SOLID = "solid"
    SOLUTION = "solution"

class SectionEnum(str, Enum):
    """Article/protocol section"""
    EXPERIMENTAL = "experimental"
    RESULTS = "results"
    METHODS = "methods"
    SUPPORTING = "supporting"
    OTHER = "other"

# 2 - Shared base types

class QtyBase(BaseModel):
    "Base for a quantity w/ units"
    value: float = Field(..., gt=0)
    unit: UnitEnum = Field(...)

class CompoundRefBase(BaseModel):
    """Base model for a chemical compound (reference)."""
    compound_id: int
    preferred_name: str = Field(..., description="Canonical name of compound")
    commercial_name: Optional[str] = Field(None, description="Commercial or usual name")
    formula: Optional[str] = Field(None, description="Chemical formula")
    smiles: Optional[str] = Field(None, description="SMILES canonical")
    molecular_weight: Optional[float] = Field(None, gt=0, description="Molecular weight (in g/mol)")
    density: Optional[float] = Field(None, gt=0, description="Density (in kg/m3)")

class SpeciesQtyBase(BaseModel):
    qty : Optional[QtyBase] = None
    moles : Optional[float] = Field(None, gt=0, description="Amount of substance (in moles)")
    millimoles: Optional[float] = Field(None, gt=0, description="Amount of substance (in millimoles)")
    equivalents: Optional[float] = Field(None, gt=0, description="Number of equivalents in respect to limiting reactant")
    concentration: Optional[float] = Field(None, gt=0, description="Concentration of solutant (in mol/L²)")
    density: Optional[float] = Field(None, gt=0, description="Density (in kg/m3)")
    purity: Optional[float] = Field(None, ge=0, le=100, description="Purity (in molar %)")
    mass_fraction: Optional[float] = Field(None, ge=0, le=100, description="Mass fraction (%)")
    molar_fraction: Optional[float] = Field(None, ge=0, le=100, description="Molar fraction (%)")
