from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
import re


class RedactRequest(BaseModel):
    """Request model for PII redaction"""
    text: str = Field(..., min_length=1, description="Input text to redact PII from")
    redact_types: Optional[List[str]] = Field(
        default=["name", "email", "phone", "address", "credit_card", "date"],
        description="Types of PII to redact"
    )
    custom_tags: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom replacement tags for different PII types"
    )

    @validator('redact_types')
    def validate_redact_types(cls, v):
        valid_types = {
            "name", "email", "phone", "address", 
            "credit_card", "date"
        }
        if not all(pii_type in valid_types for pii_type in v):
            invalid_types = [pii_type for pii_type in v if pii_type not in valid_types]
            raise ValueError(f"Invalid PII types: {invalid_types}. Valid types: {list(valid_types)}")
        return v

    @validator('custom_tags')
    def validate_custom_tags(cls, v, values):
        if v is not None:
            redact_types = values.get('redact_types', [])
            for pii_type in v.keys():
                if pii_type not in redact_types:
                    raise ValueError(f"Custom tag for '{pii_type}' provided but not in redact_types")
        return v


class RedactResponse(BaseModel):
    """Response model for PII redaction"""
    original: str = Field(..., description="Original input text")
    redacted: str = Field(..., description="Text with PII redacted")
    summary: Dict[str, int] = Field(..., description="Count of redacted entities by type")
    redact_types_used: List[str] = Field(..., description="PII types that were processed")


class FileRedactRequest(BaseModel):
    """Request model for file-based PII redaction"""
    redact_types: Optional[List[str]] = Field(
        default=["name", "email", "phone", "address", "credit_card", "date"],
        description="Types of PII to redact"
    )
    custom_tags: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom replacement tags for different PII types"
    )
    export_format: Optional[str] = Field(
        default="both",
        description="Export format: 'pdf', 'txt', or 'both'"
    )

    @validator('redact_types')
    def validate_redact_types(cls, v):
        valid_types = {
            "name", "email", "phone", "address", 
            "credit_card", "date"
        }
        if not all(pii_type in valid_types for pii_type in v):
            invalid_types = [pii_type for pii_type in v if pii_type not in valid_types]
            raise ValueError(f"Invalid PII types: {invalid_types}. Valid types: {list(valid_types)}")
        return v

    @validator('custom_tags')
    def validate_custom_tags(cls, v, values):
        if v is not None:
            redact_types = values.get('redact_types', [])
            for pii_type in v.keys():
                if pii_type not in redact_types:
                    raise ValueError(f"Custom tag for '{pii_type}' provided but not in redact_types")
        return v

    @validator('export_format')
    def validate_export_format(cls, v):
        valid_formats = ["pdf", "txt", "both"]
        if v not in valid_formats:
            raise ValueError(f"Invalid export format. Must be one of: {valid_formats}")
        return v


class FileRedactResponse(BaseModel):
    """Response model for file-based PII redaction"""
    original_text: str = Field(..., description="Original extracted text")
    redacted_text: str = Field(..., description="Text with PII redacted")
    summary: Dict[str, int] = Field(..., description="Count of redacted entities by type")
    redact_types_used: List[str] = Field(..., description="PII types that were processed")
    files_generated: List[str] = Field(..., description="List of generated file paths")
    file_sizes: Dict[str, int] = Field(..., description="File sizes in bytes")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    ollama_status: str = Field(..., description="Ollama connection status")
    model: str = Field(..., description="Currently configured model")
    timestamp: str = Field(..., description="Health check timestamp")


class FileInfo(BaseModel):
    """File information model"""
    filename: str = Field(..., description="File name")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File content type")
    upload_time: str = Field(..., description="Upload timestamp") 