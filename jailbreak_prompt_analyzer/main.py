# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(usecwd=True))
from jailbreak_prompt_analyzer.jailbreak_prompt_analyzer import (
    graph,
    AgentState,
    OutputState,
)
from jailbreak_prompt_analyzer.state import Message, Type as MsgType


def main():
    # TODO: Read the variables from the sentinel agent and currently getting the inputs from the user terminal
    #unfiltered_llm_response = " "
    #intention_analyzer_output = " "
    unfiltered_llm_response = input("Please Enter the LLM response >>>")
    intention_analyzer_output = input("Please Enter the intention analyzer output >>>")
    prompt_analyzer_input = AgentState(unfiltered_llm_response=unfiltered_llm_response,
                                       intention_analyzer_output=intention_analyzer_output)
    out = graph.invoke(prompt_analyzer_input, {"configurable": {"thread_id": "foo"}})
    output: OutputState = OutputState.model_validate(out)
    print("The List of prompts that can produce similar LLM response : \n ")
    print(output.prompt_analyzer_output)


main()
