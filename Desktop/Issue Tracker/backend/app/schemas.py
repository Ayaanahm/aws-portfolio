# backend/app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# -------------------------
# ENUMS (Match DB Enums)
# -------------------------

class PriorityEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"


class StatusEnum(str, Enum):
    Open = "Open"
    In_Progress = "In Progress"
    Resolved = "Resolved"
    Closed = "Closed"


# -------------------------
# PROJECT SCHEMAS
# -------------------------

class ProjectResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# -------------------------
# USER SCHEMAS
# -------------------------

class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]

    class Config:
        from_attributes = True


# -------------------------
# COMMENT SCHEMAS
# -------------------------

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    user_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


# -------------------------
# ISSUE SCHEMAS
# -------------------------

class IssueCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    project_id: int
    assignee_id: int
    priority: PriorityEnum
    status: StatusEnum


class IssueUpdate(BaseModel):
    status: StatusEnum


class IssueResponse(BaseModel):
    id: int
    title: str
    description: str
    project_id: int
    assignee_id: int
    priority: PriorityEnum
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class IssueListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[IssueResponse]        
        
