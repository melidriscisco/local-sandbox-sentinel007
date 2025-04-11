# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
import uuid
import asyncio
from sentinel007_agent.state import Message, Type, OverallState, ConfigModel, IntentionAnalyzerState
#from marketing_campaign.email_reviewer import TargetAudience
from agntcy_acp import AsyncACPClient, ApiClientConfiguration
from agntcy_acp.acp_v0.async_client.api_client import ApiClient as AsyncApiClient
from sentinel007_agent import intention_analyzer, jailbreak_judge, jailbreak_prompt_analyzer

from agntcy_acp.models import (
    RunCreateStateless,
    RunResult,
    RunError,
    Config,
)


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
    client_config = ApiClientConfiguration.fromEnvPrefix("SENTINEL007_")

    while True:
        usermsg = input("Please Enter your prompt to the LLM : \n")
        if usermsg == "OK":
            print("Thank you for using Sentinel007 !!")
            exit()
        # inputState.messages.append(Message(content=usermsg, type=Type.human))
        inputState.messages.append(intention_analyzer.Message(content=usermsg, type=intention_analyzer.Type.human))
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
            judge_output =outputState.jailbreak_judge_state.output.final_judgement.split("\n")[0].split(":")[1].strip()
        if judge_output == "INVALID":
            print("The given prompt looks like a jailbreaking attempt so Sentinel blocks to response")
        else:
            print("The given prompt is not jailbreaking so Sentinel allows the response")
 
            inputState = outputState



if __name__ == "__main__":
    asyncio.run(main())