# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
from typing_extensions import TypedDict
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Type(Enum):
    human = "human"
    assistant = "assistant"
    ai = "ai"


class Message(BaseModel):
    type: Type = Field(
        ...,
        description="indicates the originator of the message, a human or an assistant",
    )
    content: str = Field(..., description="the content of the message")


class ConfigSchema(BaseModel):
    test: bool


class AgentState(BaseModel):
    # messages: Optional[List[Message]] = None
    unfiltered_llm_response: Optional[str] = None
    intention_analyzer_output: Optional[str] = None


class OutputState(AgentState):
    # messages: Optional[List[Message]] = Field(None, title="Messages")
    prompt_analyzer_output: Optional[str] = Field(
        default=None, description="List of prompts tom produce same LLM response."
    )
    ia_is_completed: Optional[bool] = None
