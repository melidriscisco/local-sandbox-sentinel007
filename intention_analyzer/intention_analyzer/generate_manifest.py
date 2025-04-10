# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
from cgitb import text
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
)


manifest = AgentManifest(
    metadata=AgentMetadata(
        ref=AgentRef(name="org.agntcy.intention-analyzer", version="0.0.1", url=None),
        description= "Analyzes the intent of a given text. Final output is the intent that could be used to be passed to the Judge."),
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
                root = SourceCodeDeployment(
                    type="source_code",
                    name="intention-analyzer",
                    url=AnyUrl("https://github.com/melidriscisco/local-sandbox-sentinel007/tree/main/intention_analyzer"),
                    framework_config=LangGraphConfig(
                        framework_type="langgraph",
                        graph="intention_analyzer.intention_analyzer:graph"
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
        dependencies=[]
    )
)

with open(f"{Path(__file__).parent}/../deploy/intentionanalyzer.json", "w") as f:
    f.write(manifest.model_dump_json(
        exclude_unset=True,
        exclude_none=True,
        indent=2
    ))
