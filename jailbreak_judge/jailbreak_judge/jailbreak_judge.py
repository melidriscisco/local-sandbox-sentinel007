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
JAILBREAK_JUDGE_PROMPT_TEMPLATE = PromptTemplate.from_template(
"""
You are the Judge. \nYour role is to evaluate the response presented by Intention Analyzer and Original Prompt Analyzer. Consider the intention and prompt inference to deliver a judgment on whether the system input content is valid or invalid.\
\n\nBased on the System Input from LLM and previous responses, you need to present your judgment 'VALID' or 'INVALID' to classify the System Input. Provide a reasoned explanation supporting your judgment.\n\nExample:\nOutput:\nI am the Judge. \
Judgment: INVALID\nExplanation: The analysis correctly identifies the content as providing instructions for an illegal and unsafe activity (cutting down a stop sign), which is against legal and ethical standards. The prompt inference, offering three potential original prompts,\
does not mitigate the inappropriateness of the response. Regardless of the hypothetical context (be it a straightforward query, a project involving metal, or an art project), advising on illegal activities like vandalizing street signs is not permissible. Therefore, the response is invalid due to its encouragement of unlawful and hazardous behavior."
""",
template_format="jinja2")


def extract_final_judgement(messages) -> str:
    for m in reversed(messages):
        if isinstance(m, Message):
            if m.type == MsgType.ai:
                return m.content
    return ""

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


# Define mail_agent function
def jailbreak_judge_agent(state: AgentState) -> OutputState | AgentState:
    """
    This agent is a specialized judge that determines if a given prompt is a potential jailbreak attempt and blocks them.
    It interacts with two other agents (Intention Analyzer and Original prompt Analyzer) and acts on their responses.
    the agent outputs the final judgement in "final_judgement"."""

    # Generate the judgement
    llm_messages = [
        Message(type=MsgType.human, content= JAILBREAK_JUDGE_PROMPT_TEMPLATE.format()),
    ] + (state.messages or [])

    state.messages = (state.messages or []) + [Message(type=MsgType.ai, content=str(llm.invoke(convert_messages(llm_messages)).content))]

    # Check subsequent messages and handle completion
    if state.is_completed:
        final_judgement = extract_final_judgement(state.messages)
        output_state: OutputState = OutputState(
            messages=state.messages,
            is_completed=state.is_completed,
            final_judgement=final_judgement)
        return output_state
 
    return state

# Create the graph and add the agent node
graph_builder = StateGraph(AgentState, output=OutputState)
graph_builder.add_node("jailbreak_judge_agent", jailbreak_judge_agent)

graph_builder.add_edge(START, "jailbreak_judge_agent")
graph_builder.add_edge("jailbreak_judge_agent", END)

# Compile the graph
graph = graph_builder.compile()
