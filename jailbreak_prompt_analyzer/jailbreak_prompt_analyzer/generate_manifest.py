# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from pydantic import AnyUrl
from state import AgentState, OutputState, ConfigSchema
from agntcy_acp.manifest import (
    AgentManifest,
    AgentMetadata,
    AgentACPSpec,
    Capabilities,
    AgentRef,
    AgentDeployment,
    DeploymentOptions,
    SourceCodeDeployment,
    LangGraphConfig,
    EnvVar,
    AgentDependency
)

manifest = AgentManifest(
    metadata=AgentMetadata(
        ref=AgentRef(name="jailbreak-prompt-analyzer", version="0.0.1", url=None),
        description="This agent analyzes the prompt intent and generates 3 different prompts that could've led to the \
             given response, for the judge to take a call on the validity of the prompt. The final output is a list of prompts "),
    specs=AgentACPSpec(
        input=AgentState.model_json_schema(),
        output=OutputState.model_json_schema(),
        config=ConfigSchema.model_json_schema(),
        capabilities=Capabilities(
            threads=False,
            callbacks=False,
            interrupts=False,
            streaming=None
        ),
        custom_streaming_update=None,
        thread_state=None,
        interrupts=None
    ),
    deployment=AgentDeployment(
        deployment_options=[
            DeploymentOptions(
                root=SourceCodeDeployment(
                    type="source_code",
                    name="jailbreak-prompt-analyzer",
                    url=AnyUrl("https://github.com/melidriscisco/local-sandbox-sentinel007/tree/main/jailbreak_prompt_analyzer"),
                    framework_config=LangGraphConfig(
                        framework_type="langgraph",
                        graph="jailbreak_prompt_analyzer.jailbreak_prompt_analyzer:graph"
                    )
                )
            )
        ],
        env_vars=[
            EnvVar(name="AZURE_OPENAI_API_KEY", desc="Azure key for the OpenAI service"),
            EnvVar(name="AZURE_OPENAI_ENDPOINT", desc="Azure endpoint for the OpenAI service"),
            EnvVar(name="AZURE_OPENAI_MODEL", desc="AZURE OPENAI MODEL"),
            EnvVar(name="OPENAI_API_VERSION", desc="OPENAI_API_VERSION")
        ],
        dependencies=[
            AgentDependency(
                name="intention-analyzer",
                ref=AgentRef(name="intention-analyzer", version="0.0.1",
                             url="../../intention_analyzer/deploy/intentionanalyzer.json"),
                # ref=AgentRef(name="org.agntcy.intention-analyzer", version="0.0.1", url=AnyUrl("file://intentionanalyzer.json")),
                deployment_option=None,
                env_var_values=None
            )
        ]
    )
)

with open(f"{Path(__file__).parent}/../deploy/jailbreakpromptanalyzer.json", "w") as f:
    f.write(manifest.model_dump_json(
        exclude_unset=True,
        exclude_none=True,
        indent=2
    ))
