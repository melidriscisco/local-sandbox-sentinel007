# Generated from ACP Descriptor org.agntcy.mail_reviewer using datamodel_code_generator.

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, RootModel


class ConfigSchema(BaseModel):
    test: bool

class Type(Enum):
    human = 'human'
    assistant = 'assistant'
    ai = 'ai'

class Message(BaseModel):
    type: Type = Field(
        ...,
        description='indicates the originator of the message, a human or an assistant',
    )
    content: str = Field(..., description='the content of the message')


class InputSchema(BaseModel):
    # intent: str = Field(
    #     ..., description='The email content to be reviewed and corrected', title='Email'
    # )
    # target_audience: TargetAudience = Field(
    #     ...,
    #     description='The target audience for the email, affecting the style of review',
    # )
    messages: Optional[list[Message]] = None
    is_completed: Optional[bool] = None
    intent_analyzer_output: Optional[str] = ""
    prompt_analyzer_output: Optional[str] = ""

class OutputSchema(InputSchema):
    final_judgement: Optional[str] = Field(default=None, description="Final judgement produced by the jailbreak judge")



# class TargetAudience(Enum):
#     general = 'general'
#     technical = 'technical'
#     business = 'business'
#     academic = 'academic'
