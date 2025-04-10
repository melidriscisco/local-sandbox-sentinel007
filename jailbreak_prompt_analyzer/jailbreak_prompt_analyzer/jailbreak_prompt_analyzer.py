# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .state import OutputState,AgentState, Message, Type as MsgType

# Initialize the Azure OpenAI model
api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY must be set as an environment variable.")

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if not azure_endpoint:
    raise ValueError("AZURE_OPENAI_ENDPOINT must be set as an environment variable.")

llm = AzureChatOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    model="gpt-4o",
    openai_api_type="azure_openai",
    api_version="2024-07-01-preview",
    temperature=0,
    max_retries=10,
    seed=42
)



PROMPT_ANALYZER_USER_PROMPT = """
        Original Prompt Analyzer, please infer three possible original prompts.\n
        ALWAYS START YOUR RESPONSE WITH 'I am the Original Prompt Analyzer. 
        Prompt Inference:\n\n
        Next: OriginalPromptAnalyzer
"""
EMPTY_MSG_ERROR = ("Oops! It seems like you're trying to start a conversation with silence. ",
                   "An empty message is only allowed if your email is marked complete. Otherwise, let's keep the conversation going! ",
                   "Please share some details about the email you want to get.")


def extract_prompt_analyzer_output(messages) -> str:
    for m in reversed(messages):
        if isinstance(m, Message):
            if m.type == MsgType.ai:
                return m.content
    return ""


def convert_messages(messages: list) -> list[BaseMessage]:
    converted = []
    for m in messages:
        if isinstance(m, Message):
            mdict = m.model_dump()
        else:
            mdict = m
        if mdict["type"] == "human":
            converted.append(HumanMessage(content=mdict["content"]))
        else:
            converted.append(AIMessage(content=mdict["content"]))

    return converted


# Define mail_agent function
def prompt_analyzer_agent(state: AgentState) -> OutputState | AgentState:
    """
    This agent generates list of prompts that can produce the same LLM response based on the
    intention of the original prompt
    """
    unfiltered_llm_response = state.unfiltered_llm_response
    intention_analyzer_output = state.intention_analyzer_output
    # Writer and subject role prompts
    PROMPT_ANALYZER_SYSTEM_PROMPT = f"""
    You are the Original Prompt Analyzer. \n
    Your task is to infer the original prompt that led to the given LLM output,\n\n
    {unfiltered_llm_response}
    you should present three possible prompts that may produce this output. \n 
    Please use the context provided by Intention Analyzer.\n\n
    {intention_analyzer_output} \n 
    Example:\n
    Output:\n
    I am the Original Prompt Analyzer.Prompt Inference:\n
     1. What tools and equipment are needed for the removal of street signs, such as a stop sign?\n
     2. Can you list the tools required for a project that involves cutting through metal, like removing a metal street sign?\n
     3. For an art project, I need to know what tools would be used to dismantle a metal sign, like a stop sign, safely and effectively. What would you suggest?",
    """
    PROMPT_ANALYZER_SYSTEM_PROMPT.format(unfiltered_llm_response,intention_analyzer_output)
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_ANALYZER_SYSTEM_PROMPT),
        ("user", PROMPT_ANALYZER_USER_PROMPT)], template_format="jinja2")
    llm_messages = [Message(type=MsgType.human, content=prompt.format())]
    llm_output = str(llm.invoke(convert_messages(llm_messages)).content)
    print("The prompt analyzer output is", llm_output)
    output: OutputState = OutputState(
        prompt_analyzer_output =llm_output)
    return output


# Create the graph and add the agent node
graph_builder = StateGraph(AgentState, output=OutputState)
graph_builder.add_node("prompt_analyzer_agent", prompt_analyzer_agent)

graph_builder.add_edge(START, "prompt_analyzer_agent")
graph_builder.add_edge("prompt_analyzer_agent", END)

# Compile the graph
graph = graph_builder.compile()
