from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class CompoundBase(BaseModel):
    preferred_name: str = Field(..., description="Canonical name of compound")
    commercial_name: Optional[str] = Field(None, description="Commercial or usual name")
    formula: Optional[str] = Field(None, description="Chemical formula")
    smiles: Optional[str] = Field(None, description="SMILES canonical")
    cas_number: Optional[str] = Field(None, description="CAS number")
    molecular_weight: Optional[float] = Field(None, gt=0)
    density: Optional[float] = Field(None, gt=0)
    purity: Optional[float] = Field(None, ge=0, le=100)
    synonyms: List[str] = Field(default_factory=List)

class CompoundCreate(CompoundBase):
    pass

class CompoundRead(CompoundBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class CompoundUpdate(CompoundBase):
    preferred_name: Optional[str] =  Field(..., description="Canonical name of compound")
    commercial_name: Optional[str] = None
    formula: Optional[str] = None
    smiles: Optional[str] = None
    cas_number: Optional[str] = None
    molecular_weight: Optional[float] = Field(None, gt=0)
    density: Optional[float] = Field(None, gt=0)
    purity: Optional[float] = Field(None, ge=0, le=100)
    synonyms: Optional[List[str]] = Field(default_factory=List)
