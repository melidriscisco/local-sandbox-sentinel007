# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
from enum import Enum
import agntcy_acp.langgraph.acp_node
from agntcy_acp.langgraph.api_bridge import APIBridgeOutput, APIBridgeInput
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from langchain_core.messages import  AIMessage, HumanMessage
from sentinel007_agent import intention_analyzer, jailbreak_judge, jailbreak_prompt_analyzer

class Type(Enum):
    human = 'human'
    assistant = 'assistant'
    ai = 'ai'

class Message(BaseModel):
    type: Type = Field(
        ...,
        description='indicates the originator of the message, a human or an assistant',
    )
    content: str = Field(..., description='the content of the message', title='Content')

class ConfigModel(BaseModel):
    test: bool

class IntentionAnalyzerState(BaseModel):
    input: Optional[intention_analyzer.InputSchema] = None
    output: Optional[intention_analyzer.OutputSchema] = None

class PromptAnalyzerState(BaseModel):
    input: Optional[jailbreak_prompt_analyzer.InputSchema] = None
    output: Optional[jailbreak_prompt_analyzer.OutputSchema] = None

class JudgeState(BaseModel):
    input: Optional[jailbreak_judge.InputSchema] = None
    output: Optional[jailbreak_judge.OutputSchema] = None

class OverallState(BaseModel):
    messages: List[intention_analyzer.Message] = Field([], description="Chat messages")
    has_intention_completed: Optional[bool] = None
    has_prompt_analyzer_completed: Optional[bool] = None
    has_judge_completed: Optional[bool] = None
    has_sender_completed: Optional[bool] = None
    intention_analyzer_state: Optional[IntentionAnalyzerState] = None
    jailbreak_prompt_analyzer_state: Optional[PromptAnalyzerState] = None
    judge_state: Optional[JudgeState] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
