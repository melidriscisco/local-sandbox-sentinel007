# Generated from ACP Descriptor org.agntcy.mail_reviewer using datamodel_code_generator.

from __future__ import annotations

from enum import Enum
from typing import List, Any, Optional

from pydantic import BaseModel, Field, RootModel

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

class ConfigSchema(RootModel[Any]):
    root: Any = Field(..., title='ConfigSchema')


class InputSchema(BaseModel):
    # messages: Optional[List[Message]] = None
    unfiltered_llm_response: Optional[str] = None
    intention_analyzer_output: Optional[str] = None


class OutputSchema(BaseModel):
    prompt_analyzer_output: Optional[str] = Field(default=None, description="List of prompts tom produce same LLM response.")



# class TargetAudience(Enum):
#     general = 'general'
#     technical = 'technical'
#     business = 'business'
#     academic = 'academic'
