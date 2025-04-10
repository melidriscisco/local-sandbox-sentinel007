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
        ref=AgentRef(name="jailbreak-judge", version="0.0.1", url=None),
        description="This agent classifies a prompt as malicious or benign based on the analysis provided by it's counterpart agents. \
         Final output is on of the two tags : \"VALID\" or \"INVALID\" followed by an explanation"),
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
                    name="jailbreak-judge",
                    url=AnyUrl("https://github.com/melidriscisco/local-sandbox-sentinel007/tree/main/jailbreak_judge"),
                    framework_config=LangGraphConfig(
                        framework_type="langgraph",
                        graph="jailbreak_judge.jailbreak_judge:graph"
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
            ),
            AgentDependency(
                name="jailbreak-prompt-analyzer",
                ref=AgentRef(name="jailbreak-prompt-analyzer", version="0.0.1",
                             url="../../intention_analyzer/deploy/jailbreakpromptanalyzer.json"),
                # ref=AgentRef(name="org.agntcy.intention-analyzer", version="0.0.1", url=AnyUrl("file://intentionanalyzer.json")),
                deployment_option=None,
                env_var_values=None
            )
        ]
    )
)

with open(f"{Path(__file__).parent}/../deploy/jailbreakjudge.json", "w") as f:
    f.write(manifest.model_dump_json(
        exclude_unset=True,
        exclude_none=True,
        indent=2
    ))
