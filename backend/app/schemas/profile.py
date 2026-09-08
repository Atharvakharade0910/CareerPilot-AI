from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class Registration(Credentials):
    full_name: str = Field(min_length=2, max_length=120)
    gender: str = Field(default="prefer_not_to_say", max_length=40)


class Personal(BaseModel):
    full_name: str = Field(default="", max_length=120)
    gender: str = Field(default="prefer_not_to_say", max_length=40)
    phone: str = Field(default="", max_length=40)
    location: str = Field(default="", max_length=160)


class Preferences(BaseModel):
    target_roles: list[str] = Field(default_factory=list, max_length=15)
    locations: list[str] = Field(default_factory=list, max_length=15)
    work_type: str = Field(default="remote", pattern="^(remote|hybrid|onsite|any)$")
    experience_level: str = Field(default="entry", pattern="^(entry|mid|senior)$")
    minimum_match: int = Field(default=75, ge=0, le=100)
    relocation: bool = False


class ProfileUpdate(BaseModel):
    personal: Personal
    preferences: Preferences
    reviewed: bool = False


class EvidenceField(BaseModel):
    value: str
    category: str
    evidence: str
    confidence: float = Field(ge=0, le=1)


class Extraction(BaseModel):
    fields: list[EvidenceField]
    warnings: list[str]
    parser: str = "evidence-rules-v1"
