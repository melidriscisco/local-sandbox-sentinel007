# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
import asyncio
from sentinel007_agent.app import graph
from sentinel007_agent.state import OverallState, ConfigModel, IntentionAnalyzerState
# from marketing_campaign.email_reviewer import TargetAudience
from langchain_core.runnables.config import RunnableConfig


async def main():
    print("What do you want to ask the agent?")
    inputState = OverallState(
        messages=[],
        operation_logs=[],
        has_composer_completed=False
    )
    while True:
        usermsg = input("YOU [Type OK when you are happy with the email proposed] >>> ")
        inputState.messages.append(IntentionAnalyzerState.Message(content=usermsg, type=IntentionAnalyzerState.Type.human))
        output = await graph.ainvoke(inputState, RunnableConfig(
            configurable=ConfigModel(
                recipient_email_address=os.environ["RECIPIENT_EMAIL_ADDRESS"],
                sender_email_address=os.environ["SENDER_EMAIL_ADDRESS"],
                # target_audience=TargetAudience.academic
            ).model_dump()
        )
)

        outputState = OverallState.model_validate(output)
        if len(outputState.operation_logs) > 0:
            print(outputState.operation_logs)
            break
        else:
            print(outputState.messages[-1].content)
        inputState = outputState


if __name__ == "__main__":
    asyncio.run(main())
