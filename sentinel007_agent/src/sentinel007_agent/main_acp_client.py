# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
import uuid
import asyncio
from sentinel007_agent.state import Message, Type, OverallState, ConfigModel, IntentionAnalyzerState
#from marketing_campaign.email_reviewer import TargetAudience
from agntcy_acp import AsyncACPClient, ApiClientConfiguration
from agntcy_acp.acp_v0.async_client.api_client import ApiClient as AsyncApiClient

from agntcy_acp.models import (
    RunCreateStateless,
    RunResult,
    RunError,
    Config,
)


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
    client_config = ApiClientConfiguration.fromEnvPrefix("SENTINEL007_")

    while True:
        usermsg = input("YOU [Input prompt] >>> ")
        inputState.messages.append(Message(content=usermsg, type=Type.human))
        run_create = RunCreateStateless(
            agent_id=sentinel_id,
            input=inputState.model_dump(),
            config=Config()
        )
        async with AsyncApiClient(configuration=client_config) as api_client:
            acp_client = AsyncACPClient(api_client=api_client)
            run_output = await acp_client.create_and_wait_for_stateless_run_output(run_create)
            if run_output.output is None:
                raise Exception("Run output is None")
            actual_output = run_output.output.actual_instance
            if isinstance(actual_output, RunResult):
                run_result: RunResult = actual_output
            elif isinstance(actual_output, RunError):
                run_error: RunError = actual_output
                raise Exception(f"Run Failed: {run_error}")
            else:
                raise Exception(f"ACP Server returned a unsupport response: {run_output}")

            runState = run_result.values # type: ignore
            outputState = OverallState.model_validate(runState)
            if len(outputState.operation_logs) > 0:
                print(outputState.operation_logs)
                break
            else:
                print(outputState.messages[-1].content)
            inputState = outputState



if __name__ == "__main__":
    asyncio.run(main())