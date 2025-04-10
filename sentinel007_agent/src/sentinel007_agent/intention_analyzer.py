# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ConfigSchema(BaseModel):
    test: bool = Field(..., title='Test')


class InputSchema(BaseModel):
    messages: Optional[List[Message]] = Field(None, title='Messages')
    is_completed: Optional[bool] = Field(None, title='Is Completed')
    session_id: Optional[str] = None
    agent_id: Optional[str] = None


class Message(BaseModel):
    type: Type = Field(
        ...,
        description='indicates the originator of the message, a human or an assistant',
    )
    content: str = Field(..., description='the content of the message', title='Content')


class OutputSchema(BaseModel):
    messages: Optional[List[Message]] = Field(None, title='Messages')
    is_completed: Optional[bool] = Field(None, title='Is Completed')
    final_intent: Optional[str] = Field(default=None, description="Final intent produced by the intent_analyzer.")


class Type(Enum):
    human = 'human'
    assistant = 'assistant'
    ai = 'ai'
