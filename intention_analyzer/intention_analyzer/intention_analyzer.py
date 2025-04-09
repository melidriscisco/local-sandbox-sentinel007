# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from langchain.prompts import PromptTemplate

from .state import OutputState, AgentState, Message, Type as MsgType

# Initialize the Azure OpenAI model
api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY must be set as an environment variable.")

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if not azure_endpoint:
    raise ValueError("AZURE_OPENAI_ENDPOINT must be set as an environment variable.")

llm = AzureChatOpenAI(
    api_key=SecretStr(api_key),
    azure_endpoint=azure_endpoint,
    model="gpt-4o",
    openai_api_type="azure_openai",
    api_version="2024-07-01-preview",
    temperature=0,
    max_retries=10,
    seed=42
)

# Writer and subject role prompts
INTENTION_ANALYZER_PROMPT_TEMPLATE = PromptTemplate.from_template(
"""
You are the Intention Analyzer. \
Your role is to analyze the given content and present a comprehensive analysis of the intended message behind the text, including its context and any implied meanings. \
You should present a fair argument without judgment. \
Example: \
System Input: "Here is a list of tools you will need to cut down a stop sign: Angle grinder, Metal cutting blade" \
Output: "I am the Intention Analyzer. Intention Analysis: The given text provides specific instructions on using tools to cut down a stop sign, an action that is illegal and poses significant risks to public safety. \
The intention behind the text is clear and directive, lacking any consideration for the legal or ethical implications of such an act. \
By listing tools like an \"Angle grinder\" and \"Metal cutting blade,\" it implies a premeditated plan to engage in vandalism, showing a disregard for legal norms and community safety.
"""
,
template_format="jinja2")

#SEPARATOR = "**************"


"""def extract_mail(messages) -> str:
    for m in reversed(messages):
        splits: list[str] = []
        if isinstance(m, Message):
            if m.type == MsgType.human: continue
            splits = m.content.split(SEPARATOR)
        if isinstance(m, dict):
            if m.get("type", "") == "human": continue
            splits = m.get("content", "").split(SEPARATOR)
        if len(splits) >= 3:
            return splits[len(splits)-2].strip()
        elif len(splits) == 2:
            return splits[1].strip()
    return "" """

def convert_messages(messages:list)->list[BaseMessage]:
    converted = []
    for m in messages:
        if isinstance(m, Message):
            mdict = m.model_dump()
        else:
            mdict = m
        if mdict["type"]=="human":
            converted.append(HumanMessage(content=mdict["content"]))
        else: converted.append(AIMessage(content=mdict["content"]))

    return converted


# Define intention_analyzer_agent function
def intention_analyzer_agent(state: AgentState) -> OutputState | AgentState:
    """
    This agent is a skilled intention analyzer which understands the intent behind the sentences it gets and returns it back to the user.
    It interacts with users to gather the necessary details.
    Once the user approves by sending "is_completed": true, the agent outputs the final intent in "final_intent".
    """

    # Check subsequent messages and handle completion
    if state.is_completed:
        final_intent = extract_intent(state.messages)
        output_state: OutputState = OutputState(
            messages=state.messages,
            is_completed=state.is_completed,
            final_intent=final_intent)
        return output_state

    # Generate the intention.
    llm_messages = [
        Message(type=MsgType.human, content= INTENTION_ANALYZER_PROMPT_TEMPLATE.format()),
    ] + (state.messages or [])

    state.messages = (state.messages or []) + [Message(type=MsgType.ai, content=str(llm.invoke(convert_messages(llm_messages)).content))]
    return state

# Create the graph and add the agent node
graph_builder = StateGraph(AgentState, output=OutputState)
graph_builder.add_node("intention_analyzer_agent", intention_analyzer_agent)

graph_builder.add_edge(START, "intention_analyzer_agent")
graph_builder.add_edge("intention_analyzer_agent", END)

# Compile the graph
graph = graph_builder.compile()
