from pydantic import BaseModel, Field
from typing import Optional

# Pydantic models for structured extraction matching the schema
class Subsection(BaseModel):
    subsection_number: str = Field(description="The subsection number (e.g., 3.1.1, 5.1.2.1).")
    description: str = Field(description="A description of the law or regulation within the subsection. Do not include the section number in the description.")

class Section(BaseModel):
    section_number: str = Field(description="The section number (e.g., 1.1, 2.1, 3.1).")
    description: str = Field(description="A description of the law or regulation within the section. Do not include the section number in the description.")
    subsections: Optional[list[Subsection]] = Field(default=None, description="An array of subsections within the section.")

class LawCategory(BaseModel):
    title: str = Field(description="The title of the law category (e.g., Peace, Religion, Widows). Do not include the number in the title.")
    number: int = Field(description="The number of the law category (e.g., 1, 2, 3).")
    sections: list[Section] = Field(description="An array of sections within the law category.")

class LawsDocument(BaseModel):
    laws: list[LawCategory] = Field(description="An array of law categories.")