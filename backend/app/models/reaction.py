from pydantic import BaseModel, Field
from typing import Optional, List
from backend.app.models.common import RoleEnum, CompoundRefBase

class ReactionBase(BaseModel):
    """Reaction descriptors"""
    name: Optional[str] = Field(None, description="Reaction name")
    target_yield: Optional[float] = Field(None, ge=0, le=100, description="Targeted or reported yield (%)")
    scale: Optional[float] = Field(None, gt=0, description="Scale of the reaction (e.g., amount of the limiting reactant)")
    scale_unit: Optional[str] = Field(None,  description="Unit scale (e.g.: mmol, g)")

class ReactionSpeciesBase(BaseModel):
    """Commonly shared properties of all reactant species"""
    compound_id : int = Field(..., description="DB's ID of compound")

    role : RoleEnum = Field(..., description="Role of the species in the reaction (e.g., reactant, product, catalyst)")
    coeff : float = Field(..., gt=0, description="Stoichiometric coefficient")

    quantity : Optional[float] = Field(None, description="Quantity of the species in moles")
    unit : Optional[str] = Field(None, description="Unit of the quantity (e.g., moles, grams)")
    equivalents : Optional[float] = Field(None, description="Equivalents of the species in the reaction")
    concentration : Optional[float] = Field(None, description="Concentration of the species in the reaction")
    density: Optional[float] = Field(None, gt=0, description="Density to convert volume to mass")
    purity: Optional[float] = Field(None, ge=0, le=100, description="Purity (%)")
    mass_fraction : Optional[float] = Field(None, ge=0, le=100, description="Mass fraction of compound (in mass %)")
    molar_fraction : Optional[float] = Field(None, ge=0, le=100, description="Molar fraction of compound (in mole %)")

class RectionSpeciesCreate(ReactionSpeciesBase):
    """To create a reaction species"""
    raw_compound_name : Optional[str] = Field(None, description="Raw name of the compound if not in the database")

class ReactionSpeciesRead(ReactionSpeciesBase):
    """Expected format of response for a reactions species API call"""
    id: int

    compound: Optional[CompoundRefBase] = None

    calculated_moles : Optional[float] = Field(None, ge=0, description="Calculated moles amount")
    calculated_mass : Optional[float] = Field(None, ge=0, description="Theoretical calculated mass")

    model_config = {"from_attributes": True}

class ReactionConditionBase(BaseModel):
    """Operationg conditions of reaction"""
    temperature: Optional[float] = Field(None, description="Temperature")
    temperature_unit: Optional[str] = Field("C", description="Temperature unit (Celsius, Kelvin...")
    duration_hours : Optional[float] = Field(None, description="Duration (in hours)")
    duration_mins : Optional[float] = Field(None, description="Duration (in minutes)")
    atmosphere: Optional[str] = Field(None, description="e.g.: Argon, Nitrogen, Air")

class ReactionCreate(ReactionBase):
    """Reaction creation API call"""
    species: List[RectionSpeciesCreate] = Field(default_factory=list, description="List of engaged reaction species")
    conditions: Optional[ReactionConditionBase] = Field(None, description="Reaction conditions")

class ReactionRead(ReactionBase):
    """Expected response output for a reaction species API call"""
    id: int

    species: List[ReactionSpeciesRead] = Field(default_factory=list, description="List of engaged reaction species")
    conditions: Optional[ReactionConditionBase] = Field(None, description="Reaction conditions")

    theoretical_yield_mass: Optional[float] = Field(None, description="Theoretical calculated mass")
    limiting_reagent_id: Optional[int] = Field(None, description="Reaction species' ID of identified limiting reactant")

    model_config = {"from_attributes": True}
