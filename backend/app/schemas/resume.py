from __future__ import annotations

from pydantic import BaseModel


class EducationItem(BaseModel):
    school: str
    major: str = ""
    degree: str = ""
    status: str = ""


class CareerItem(BaseModel):
    company: str
    period: str = ""
    role: str = ""


class ResumeExtractResult(BaseModel):
    name: str
    birth_date: str = ""
    phone: str
    email: str
    address: str = ""
    total_years_experience: float
    education: list[EducationItem]
    career: list[CareerItem]
    certifications: list[str]
    languages: list[str] = []
    military_service: str = ""
    desired_position: str = ""
    desired_salary: str = ""
    desired_location: str = ""
    notes: str = ""
