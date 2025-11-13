"""
Pydantic models for request validation and type checking
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional


class StudentCreate(BaseModel):
    """Schema for creating a new student"""
    id: str = Field(..., min_length=1, max_length=50, description="Student ID")
    name: str = Field(..., min_length=1, max_length=100, description="Student name")
    email: EmailStr = Field(..., description="Student email address")
    
    @validator('id')
    def validate_id(cls, v):
        if not v.strip():
            raise ValueError('Student ID cannot be empty or whitespace')
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "2022CS001",
                "name": "Alice Johnson",
                "email": "alice@university.edu"
            }
        }


class RecognitionCreate(BaseModel):
    """Schema for creating a recognition (credit transfer)"""
    sender_id: str = Field(..., min_length=1, max_length=50, description="Sender student ID")
    recipient_id: str = Field(..., min_length=1, max_length=50, description="Recipient student ID")
    credits: int = Field(..., gt=0, le=100, description="Credits to transfer (1-100)")
    message: Optional[str] = Field(None, max_length=500, description="Recognition message")
    
    @validator('sender_id', 'recipient_id')
    def validate_ids(cls, v):
        if not v.strip():
            raise ValueError('Student ID cannot be empty or whitespace')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "2022CS001",
                "recipient_id": "2022CS002",
                "credits": 15,
                "message": "Great job on the project!"
            }
        }


class EndorsementCreate(BaseModel):
    """Schema for creating an endorsement"""
    recognition_id: int = Field(..., gt=0, description="Recognition ID to endorse")
    endorser_id: str = Field(..., min_length=1, max_length=50, description="Endorser student ID")
    
    @validator('endorser_id')
    def validate_endorser_id(cls, v):
        if not v.strip():
            raise ValueError('Endorser ID cannot be empty or whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "recognition_id": 1,
                "endorser_id": "2022CS003"
            }
        }


class RedemptionCreate(BaseModel):
    """Schema for creating a redemption"""
    student_id: str = Field(..., min_length=1, max_length=50, description="Student ID")
    credits: int = Field(..., gt=0, description="Credits to redeem")
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v.strip():
            raise ValueError('Student ID cannot be empty or whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "2022CS002",
                "credits": 10
            }
        }

