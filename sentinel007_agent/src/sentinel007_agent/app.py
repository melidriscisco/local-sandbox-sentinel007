# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
import json
import copy
from agntcy_iomapper import IOMappingAgent, IOMappingAgentMetadata
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from agntcy_acp.langgraph.acp_node import ACPNode
from agntcy_acp.langgraph.io_mapper import add_io_mapped_edge
from agntcy_acp import ApiClientConfiguration
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_core.runnables import RunnableConfig
from langchain_openai.chat_models.azure import AzureChatOpenAI
from sentinel007_agent import (
    intention_analyzer,
    state,
    jailbreak_judge,
    jailbreak_prompt_analyzer,
)
from sentinel007_agent.state import (
    IntentionAnalyzerState,
    PromptAnalyzerState,
    JudgeState,
)

# Fill in client configuration for the remote agent
INTENTION_ANALYZER_AGENT_ID = os.environ.get("INTENTION_ANALYZER_ID", "")
PROMPT_ANALYZER_AGENT_ID = os.environ.get("PROMPT_ANALYZER_ID", "")
JAILBREAK_JUDGE_AGENT_ID = os.environ.get("JAILBREAK_JUDGE_ID", "")
INTENTION_ANALYZER_CLIENT_CONFIG = ApiClientConfiguration.fromEnvPrefix(
    "INTENTION_ANALYZER_"
)
PROMPT_ANALYZER_CLIENT_CONFIG = ApiClientConfiguration.fromEnvPrefix("PROMPT_ANALYZER_")
JAILBREAK_JUDGE_CLIENT_CONFIG = ApiClientConfiguration.fromEnvPrefix("JAILBREAK_JUDGE_")

# Set to True to generate a mermaid graph
GENERATE_MERMAID_GRAPH = (
        os.environ.get("GENERATE_MERMAID_GRAPH", "False").lower() == "true"
)


def process_intention_analyzer_input(
        state: state.OverallState, config: RunnableConfig
) -> state.OverallState:
    cfg = config.get("configurable", {})
    state.has_intention_completed = True
    state.intention_analyzer_state = IntentionAnalyzerState(
        input=intention_analyzer.InputSchema(
            messages=copy.deepcopy(state.messages),
            is_completed=state.has_intention_completed,
        )
    )
    return state


async def process_prompt_analyzer_input(
        state: state.OverallState, config: RunnableConfig
):
    intent = state.intention_analyzer_state.output.final_intent
    state.has_prompt_analyzer_completed = True
    state.jailbreak_prompt_analyzer_state = PromptAnalyzerState(
        input=jailbreak_prompt_analyzer.InputSchema(
            unfiltered_llm_response=copy.deepcopy(state.messages[-1].content),
            intention_analyzer_output=intent,
        )
    )
    return state


def process_judge_input(state: state.OverallState, config: RunnableConfig):
    state.has_judge_completed = True
    prompt_analyzer_output = state.jailbreak_prompt_analyzer_state.output.prompt_analyzer_output
    intention_analyzer_output = state.intention_analyzer_state.output.final_intent
    state.jailbreak_judge_state = JudgeState(
        input=jailbreak_judge.InputSchema(intent_analyzer_output=str(intention_analyzer_output),
                                          prompt_analyzer_output=str(prompt_analyzer_output),
                                          is_completed = state.has_judge_completed
                                          )
    )
    return state


def build_graph() -> CompiledStateGraph:
    llm = AzureChatOpenAI(
        model="gpt-4o-mini",
        api_version="2024-07-01-preview",
        seed=42,
        temperature=0,
    )

    # Instantiate the local ACP node for the remote agent
    acp_intention_analyzer = ACPNode(
        name="intention_analyzer",
        agent_id=INTENTION_ANALYZER_AGENT_ID,
        client_config=INTENTION_ANALYZER_CLIENT_CONFIG,
        input_path="intention_analyzer_state.input",
        input_type=intention_analyzer.InputSchema,
        output_path="intention_analyzer_state.output",
        output_type=intention_analyzer.OutputSchema,
    )
    acp_prompt_analyzer = ACPNode(
        name="jailbreak_prompt_analyzer",
        agent_id=PROMPT_ANALYZER_AGENT_ID,
        client_config=PROMPT_ANALYZER_CLIENT_CONFIG,
        input_path="jailbreak_prompt_analyzer_state.input",
        input_type=jailbreak_prompt_analyzer.InputSchema,
        output_path="jailbreak_prompt_analyzer_state.output",
        output_type=jailbreak_prompt_analyzer.OutputSchema,
    )
    acp_judge = ACPNode(
        name="jailbreak_judge",
        agent_id=JAILBREAK_JUDGE_AGENT_ID,
        client_config=JAILBREAK_JUDGE_CLIENT_CONFIG,
        input_path="jailbreak_judge_state.input",
        input_type=jailbreak_judge.InputSchema,
        output_path="jailbreak_judge_state.output",
        output_type=jailbreak_judge.OutputSchema,
    )

    # Create the state graph
    sg = StateGraph(state.OverallState)

    # Add nodes
    sg.add_node("process_inputs", process_intention_analyzer_input)
    sg.add_node(acp_intention_analyzer)
    sg.add_node("preparing prompt analyzer input", process_prompt_analyzer_input)
    sg.add_node(acp_prompt_analyzer)
    sg.add_node("preparing judge input", process_judge_input)
    sg.add_node(acp_judge)
    # sg.add_node("process final judgement", check_final_response)
    # Add edges
    sg.add_edge(START, "process_inputs")
    sg.add_edge("process_inputs", acp_intention_analyzer.get_name())
    sg.add_edge(acp_intention_analyzer.get_name(), "preparing prompt analyzer input")
    sg.add_edge("preparing prompt analyzer input", acp_prompt_analyzer.get_name())
    sg.add_edge(acp_prompt_analyzer.get_name(), "preparing judge input")
    sg.add_edge("preparing judge input", acp_judge.get_name())
    # sg.add_edge(acp_judge.get_name(),"process final judgement" )
    g = sg.compile()
    g.name = "Sentinel 007"
    if GENERATE_MERMAID_GRAPH:
        with open("___graph.png", "wb") as f:
            f.write(
                g.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            )
    return g
graph = build_graph()
