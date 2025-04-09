# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import agntcy_acp.langgraph.acp_node
from agntcy_acp.langgraph.api_bridge import APIBridgeOutput, APIBridgeInput
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from langchain_core.messages import  AIMessage, HumanMessage
from sentinel007 import intention_analyzer, jailbreak_judge, jailbreak_prompt_analyzer

class ConfigModel(BaseModel):
    recipient_email_address: str = Field(..., description="Email address of the email recipient")
    sender_email_address: str = Field(..., description="Email address of the email sender")
    # target_audience: email_reviewer.TargetAudience = Field(..., description="Target audience for the marketing campaign")

class IntentionAnalyzerState(BaseModel):
    input: Optional[intention_analyzer.InputSchema] = None
    output: Optional[intention_analyzer.OutputSchema] = None

class PromptAnalyzerState(BaseModel):
    input: Optional[jailbreak_prompt_analyzer.InputSchema] = None
    output: Optional[jailbreak_prompt_analyzer.OutputSchema] = None

class JudgeState(BaseModel):
    input: Optional[jailbreak_judge.InputSchema] = None
    output: Optional[jailbreak_judge.OutputSchema] = None

class SendGridState(BaseModel):
    input: Optional[APIBridgeInput] = None
    output: Optional[APIBridgeOutput]= None

class OverallState(BaseModel):
    messages: List[intention_analyzer.Message] = Field([], description="Chat messages")
    operation_logs: List[str] = Field([],
                                      description="An array containing all the operations performed and their result. Each operation is appended to this array with a timestamp.",
                                      examples=[["Mar 15 18:10:39 Operation performed: email sent Result: OK",
                                                 "Mar 19 18:13:39 Operation X failed"]])

    has_intention_completed: Optional[bool] = Field(None, description="Flag indicating if the intention analyzer has succesfully completed its task")
    has_prompt_analyzer_completed: Optional[bool] = None
    has_judge_completed: Optional[bool] = None
    has_sender_completed: Optional[bool] = None
    intention_analyzer_state: Optional[IntentionAnalyzerState] = None
    prompt_analyzer_state: Optional[PromptAnalyzerState] = None
    jailbreak_judge_state: Optional[JudgeState] = None
    #target_audience: Optional[email_reviewer.TargetAudience] = None
    sendgrid_state: Optional[SendGridState] = None
