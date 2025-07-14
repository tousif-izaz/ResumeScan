"""
MCP Data Models
Clean, type-safe data structures for resume processing
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class ResumeSection(str, Enum):
    """Resume section types"""
    CONTACT = "contact"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"


class ResumeBlock(BaseModel):
    """A block of resume content with metadata"""
    content: str = Field(description="The text content")
    section: ResumeSection = Field(description="Which section this belongs to")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    confidence: float = Field(default=1.0, description="Confidence score (0-1)")


class ContactInfo(BaseModel):
    """Extracted contact information"""
    name: Optional[str] = Field(default=None, description="Full name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="Location/City")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn URL")


class ParsedResume(BaseModel):
    """Complete parsed resume data"""
    raw_text: str = Field(description="Original raw text")
    contact_info: ContactInfo = Field(description="Extracted contact information")
    sections: Dict[ResumeSection, List[ResumeBlock]] = Field(
        description="Parsed sections with blocks"
    )
    all_keywords: List[str] = Field(default_factory=list, description="All extracted keywords")
    file_path: Optional[str] = Field(default=None, description="Source file path")


class ParseResult(BaseModel):
    """Result of resume parsing operation"""
    success: bool = Field(description="Whether parsing was successful")
    resume: Optional[ParsedResume] = Field(default=None, description="Parsed resume data")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    messages: List[str] = Field(default_factory=list, description="Processing messages") 