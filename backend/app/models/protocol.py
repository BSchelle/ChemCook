from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from common import QtyBase

### Individual protocol step

class ProtocolStepBase(BaseModel):
    order : int = Field(..., ge=1, description="Step order index")
    action : str = Field(..., description="Step name")
    description : Optional[str] = Field(None, description="Description of performed step")
    temperature_C : Optional[float] = Field(None, description="Temperature of step (in C)")
    duration_min : Optional[float] = Field(None, description="Duration of step (in min)")
    compounds_involved: List[int] = Field(default_factory=list, description="List of IDs of involved compounds")
    quantities: Optional[List[QtyBase]] = Field(None, description="List of quantities of involved compounds")

class ProtocolStepCreate(ProtocolStepBase):
    pass

class ProtocolStepRead(ProtocolStepBase):
    id: int
    created_at: datetime

### Global multistep protocol
class ProtocolBase(BaseModel):
    title : Optional[str] = Field(None, description="Name of the protocol")
    reaction_id : Optional[int] = Field(None, description="Reaction ID")
    steps : List[ProtocolStepBase] = Field(min_length=1, description="List of individual protocol steps")
    source_text : Optional[str] = Field(None, description="Original text protocol")

class ProtocolCreate(ProtocolBase):
    pass

class ProtocoleRead(ProtocolBase):
    model_config = {"from_attributes": True}

    id : int
    reaction_id : Optional[int] = Field(None, ge=1, description="Reaction ID")
    created_at : datetime
    steps_read : List[ProtocolStepRead] = Field(default_factory=list, description="List of individual protocol steps")
