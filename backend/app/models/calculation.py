from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from backend.app.models.common import CompoundRefBase, RoleEnum, SpeciesQtyBase


### Classes for one species calculation

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

### Classes for global calculation

class CalculationBase(BaseModel):
    reaction_id : int
    species : List[ReactionSpeciesForCalculationBase] = Field(min_length=2, description="List of species engaged")
    target_yield_percent : Optional[float] = Field(None, ge=0, le=100, description="Expected yield percent of reaction")
    scale_factor : Optional[float] = Field (None, gt=0, description="Multiplication factor of reaction scaling")
    target_mass_product_g : Optional[float] = Field(None, gt=0, description="Expected mass of desired compound")
    primary_product_id : Optional[int] = Field(None, description="Compound ID of the primary product for yield and scale calculations")


class CalculationCreate(CalculationBase):
    pass

class AvancementRow(BaseModel):
    species_name : str
    role : RoleEnum
    coeff : float = Field(..., gt=0, description="stoichiometric amount of compound" )
    n_init : float = Field(..., ge=0, description="Initial quantity of matter of compound at t_0")
    n_final : Optional[float] = Field(None, ge=0, description="Final quantity of matter of compound t_final")
    delta_n : Optional[float] = Field(None, description="Difference of quantity of matter between t_final and t_0")


class CalculationRead(CalculationBase):
    model_config = {'from_attributes': True}

    id : int
    created_at : datetime
    updated_at :  Optional[datetime] = None

    limiting_reactant_id : Optional[int] = Field(None, description="Limiting reactant's ID")
    limiting_reactant_name: Optional[str] = Field(None, description="Limiting reactant's name")
    xmax: Optional[float] = Field(None, gt=0, description="Maximum stochiometry")
    theoretical_yield_moles: Optional[float] = Field(None, gt=0, description="Theoretical yield based on moles")
    theoretical_yield_mass_g: Optional[float] = Field(None, gt=0, description="Theoretical yield based on mass (in g)")
    species_results: List[ReactionSpeciesResult] = Field(..., description="List of obtained species")
    avancement_table: List[AvancementRow] = Field(..., description="Avancement table for the reaction")
    scaled_quantities: Optional[List[ReactionSpeciesResult]] = Field(None, description="List of species with updated features after reaction")
