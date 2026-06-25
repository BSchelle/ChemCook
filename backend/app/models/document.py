from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from backend.app.models.common import QtyBase, SectionEnum

# Document section extraction

class DocumentSectionBase(BaseModel):
    title: str = Field(..., description="Title of the section")
    section_type: SectionEnum = Field(..., description="Normalized section type")
    text: str = Field(..., description="Raw text of the section")
    page_start: Optional[int] = Field(None, ge=1, description="Starting page")
    page_end: Optional[int] = Field(None, ge=1, description="Ending page")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Extraction confidence")


#Base document extraction

class DocumentExtractionBase(BaseModel):
    source_type: str = Field(..., description="Input file format")
    source_path: Optional[str] = Field(None, description="Input file path")
    full_text: Optional[str] = Field(None, description="Input file full text")
    sections: List[DocumentSectionBase] = Field(default_factory=list, description="List of pages subsections")
    experimental_text: Optional[str] = Field(None, description="Full text experimental section informations")

# Extracted compound entity

class ExtractedCompound(BaseModel):
    name: str
    commercial_name: Optional[str] = Field(None, description="Commercial name of extracted compound")
    quantity: Optional[QtyBase] = Field(None, description="Quantity of extracted compound")
    moles: Optional[float] = Field(None, description="Quantity of extracted compound (in moles)")
    equivalents: Optional[float] = Field(None, description="Number of equivalents of extracted compound")
    confidence: float = Field(0.0, ge=0, le=1, description="Extraction confidence of compound")

# Global extraction

class DocumentExtractionCreate(DocumentExtractionBase):
    pass

class DocumentExtractionRead(DocumentExtractionBase):
    created_at: datetime
    extracted_compounds: List[ExtractedCompound] = Field(default_factory=list)
    ocr_quality: Optional[str] = Field(None, description="extraction quality for the document, \
                                       used to assess whether the extracted text should be trusted or manually reviewed")
