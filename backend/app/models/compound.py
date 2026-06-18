from pydantic import BaseModel, Field
from typing import Optional

class CompoundBase(BaseModel):
    preferred_name: str = Field(..., description="Nom canonique du composé")
    commercial_name: Optional[str] = Field(None, description="Nom commercial ou nom d'usage")
    formula: Optional[str] = Field(None, description="Formule brute")
    smiles: Optional[str] = Field(None, description="SMILES canonical")
    cas_number: Optional[str] = Field(None, description="Numéro CAS")
    molecular_weight: Optional[float] = Field(None, gt=0)
    density: Optional[float] = Field(None, gt=0)
    purity: Optional[float] = Field(None, ge=0, le=100)
    synonyms: list[str] = Field(default_factory=list)

class CompoundCreate(CompoundBase):
    pass

class CompoundRead(CompoundBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None



class CompoundUpdate(CompoundBase):
    preferred_name: Optional[str] = None
    commercial_name: Optional[str] = None
    formula: Optional[str] = None
    smiles: Optional[str] = None
    cas_number: Optional[str] = None
    molecular_weight: Optional[float] = Field(None, gt=0)
    density: Optional[float] = Field(None, gt=0)
    purity: Optional[float] = Field(None, ge=0, le=100)
    synonyms: Optional[list[str]] = None
