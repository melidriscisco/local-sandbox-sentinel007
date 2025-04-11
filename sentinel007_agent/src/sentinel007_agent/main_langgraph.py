# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
import uuid
import asyncio
from sentinel007_agent.app import graph
from sentinel007_agent.state import  Message, Type, OverallState, ConfigModel, IntentionAnalyzerState
from sentinel007_agent import intention_analyzer, jailbreak_judge, jailbreak_prompt_analyzer
# from marketing_campaign.email_reviewer import TargetAudience
# from langchain_core.runnables.config import RunnableConfig


async def main():
    session_uuid = str(uuid.uuid4())
    sentinel_id = os.environ.get("SENTINEL007_ID", "")
    inputState = OverallState(
        messages=[],
        operation_logs=[],
        has_intention_completed=True,
        has_prompt_analyzer_completed=False,
        has_judge_completed=False,
        session_id= session_uuid,
        agent_id= sentinel_id
    )
    while True:
        usermsg = input("Please Enter your prompt to the LLM : \n")
        if usermsg == "OK":
            print("Thank you for using Sentinel007 !!")
            exit()
        inputState.messages.append(intention_analyzer.Message(content=usermsg, type=intention_analyzer.Type.human))
        output = await graph.ainvoke(inputState)
        outputState = OverallState.model_validate(output)
        judge_output =outputState.jailbreak_judge_state.output.final_judgement.split("\n")[0].split(":")[1].strip()
        if judge_output == "INVALID":
            print("The given prompt looks like a jailbreaking attempt so Sentinel blocks to response")
        else:
            print("The given prompt is not jailbreaking so Sentinel allows the response")
        inputState = outputState

if __name__ == "__main__":
    asyncio.run(main())
