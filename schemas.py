# schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class PostAnalysisInput(BaseModel):
    content: str = Field(..., description="Raw post text OR a LinkedIn post URL")

class ProfileAnalysisInput(BaseModel):
    file: str = Field(..., description="Path to the Excel file")
    question: Optional[str] = Field("", description="Optional analysis question/instructions")

class CreatePostInput(BaseModel):
    topic: str = Field(..., description="Post topic or idea")
    post_type: str = Field(..., description="One of: general, story, question, insight, achievement")

class SendEmailInput(BaseModel):
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    to: str = Field(..., description="Recipient email address")
    
