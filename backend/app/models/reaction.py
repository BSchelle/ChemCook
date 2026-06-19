from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID

class ReactionSpeciesBase(BaseModel):
    """Commonly shared properties of all reactant species"""
    role : str = Field(..., description="Role of the species in the reaction (e.g., reactant, product, catalyst)")
    quantity : Optional[float] = Field(None, description="Quantity of the species in moles")
    unit : Optional[str] = Field(None, description="Unit of the quantity (e.g., moles, grams)")
    equivalents : Optional[float] = Field(None, description="Equivalents of the species in the reaction")
    concentration : Optional[float] = Field(None, description="Concentration of the species in the reaction")

class RectionSpeciesCreate(ReactionSpeciesBase):
    """To create a reaction species"""
    compound_id:Optional[UUID] = Field(None, description="ID of the compound associated with the species")
    raw_compound_name:Optional[str] = Field(None, description="Raw name of the compound if not in the database")

class ReactionSpeciesRead(ReactionSpeciesBase):
    """Expected format of response for a reactions species API call"""
    id: UUID
    compound_id : Optional[UUID] = None

    calculated_moles : Optional[float] = Field(None, description="Calculated moles amount")
    calculated_mass : Optional[float] = Field(None, description="Theoretical calculated mass")

    model_config = ConfigDict(from_attributes=True)

class ReactionConditionBase(BaseModel):
    """Operationg conditions of reaction"""
    temperature: Optional[float] = None
    temperature_unit: Optional[str] = "C"
    duration_hours: Optional[float] = None
    atmosphere: Optional[str] = Field(None, description="e.g.: Argon, Nitrogen, Air")


class ReactionBase(BaseModel):
    """Reaction descriptors"""
    name: Optional[str] = Field(None, description="Reaction name")
    target_yield: Optional[float] = Field(None, description="Targeted or reported yield (%)")
    scale: Optional[float] = Field(None, description="Scale of the reaction (e.g., amount of the limiting reactant)")
    scale_unit: Optional[str] = Field(None, description="Unit scale (e.g.: mmol, g)")

class ReactionCreate(ReactionBase):
    """Reaction creation API call"""
    species: List[RectionSpeciesCreate] = Field(default_factory=list)
    conditions: Optional[ReactionConditionBase] = None

class ReactionRead(ReactionBase):
    """Exoected response output for a reaction species API call"""
    id: UUID
    species: List[ReactionSpeciesRead] = Field(default_factory=list)
    conditions: Optional[ReactionConditionBase] = None

    # Champs enrichis/calculés au niveau de la réaction
    theoretical_yield_mass: Optional[float] = Field(None, description="Theoretical calculated mass")
    limiting_reagent_id: Optional[UUID] = Field(None, description="Reaction species' ID of identified limiting reactant")

    model_config = ConfigDict(from_attributes=True)
