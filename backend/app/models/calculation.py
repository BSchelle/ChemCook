from pydantic import BaseModel, Field
from typing import Optional, List
from common import CompoundRefBase, RoleEnum, SpeciesQtyBase

class ReactionSpeciesForCalculationBase(BaseModel):
    """Reaction species for calculation"""
    compound : CompoundRefBase = Field(..., description="Descriptors of a compound")
    role : RoleEnum = Field(..., description="Role in the reaction process")
    coeff : float = Field(..., gt=0, description="Stoechiometric coefficient")
    qty : SpeciesQtyBase = Field(..., description="Quantity of said compound")

class ReactionSpeciesForCalculationCreate(ReactionSpeciesForCalculationBase):
    pass

class ReactionSpeciesResult(ReactionSpeciesForCalculationBase):
    """Expected output from calculation API call"""
    limiting_reactant : bool = False
    initial_moles : Optional[float] = Field(None, gt=0)
    final_moles : Optional[float] = None
    theoretical_yield_moles : Optional[float] = Field(None, gt=0)
    theoretical_yield_mass : Optional[float] = Field(None, gt=0)
    required_mass_g :  Optional[float] = Field(None, gt=0)
    required_volume_mL :  Optional[float] = Field(None, gt=0)
