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
    print("What do you want to ask the agent?")
    session_uuid = str(uuid.uuid4())
    print("Session UUID:", session_uuid)
    sentinel_id = os.environ.get("SENTINEL007_ID", "")
    print("sentinel_id",sentinel_id)
    inputState = OverallState(
        messages=[],
        operation_logs=[],
        has_intention_completed=False,
        has_prompt_analyzer_completed=False,
        has_judge_completed=False,
        session_id= session_uuid,
        agent_id= sentinel_id
    )
    while True:
        usermsg = input("YOU >>> ")
        # inputState.messages.append(IntentionAnalyzerState.Message(content=usermsg, type=IntentionAnalyzerState.Type.human))
        print("sekljfnvwe;klnvkwev:",inputState.messages)
        inputState.messages.append(intention_analyzer.Message(content=usermsg, type=intention_analyzer.Type.human))
        output = await graph.ainvoke(inputState)

        outputState = OverallState.model_validate(output)

        print(outputState.messages[-1].content)
        inputState = outputState
        print("WOHOOO")

if __name__ == "__main__":
    asyncio.run(main())
