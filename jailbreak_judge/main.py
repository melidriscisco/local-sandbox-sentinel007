# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import json

from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(usecwd=True))
from jailbreak_judge.jailbreak_judge import graph, AgentState, OutputState
from jailbreak_judge.state import Message, Type as MsgType


def main():
    output = OutputState(messages=[], final_judgement=None)

    # Currently intent_analyzer_output and prompt_analyzer_output are being read from the console
    # Once sentinel007 is updated, it'll populate these variables from the outputs of the other agents
    # TODO : Read these from sentinel007
    
    intent_analyzer_output = input("YOU [Enter the intent analyzer's output:] >>> ")

    prompt_analyzer_output = input("YOU [Enter the prompt analyzer's output:] >>> ")

    message = """
            Intention Analyzer response : {} \n
            Original Prompt Analyzer : {} \n
            """.format(intent_analyzer_output, prompt_analyzer_output)
    

    nextinput = AgentState(
        messages=(output.messages or [])
        + [Message(content=message, type=MsgType.human)]
    )
    nextinput.is_completed = True
    out = graph.invoke(nextinput, {"configurable": {"thread_id": "foo"}})
    output: OutputState = OutputState.model_validate(out) 


    print("Final judgement is:")
    print(output.final_judgement)


main()
