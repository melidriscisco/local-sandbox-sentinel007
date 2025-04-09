# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from pydantic import AnyUrl
from sentinel007.state import OverallState, ConfigModel
from agntcy_acp.manifest import (
    AgentManifest,
    AgentDeployment,
    DeploymentOptions,
    LangGraphConfig,
    EnvVar,
    AgentMetadata,
    AgentACPSpec,
    AgentRef,
    Capabilities,
    SourceCodeDeployment,
    AgentDependency
)


manifest = AgentManifest(
    metadata=AgentMetadata(
        ref=AgentRef(name="org.agntcy.sentinel007", version="0.0.1", url=None),
        description="Jailbreak Defense Agent"),
    specs=AgentACPSpec(
        input=OverallState.model_json_schema(),
        output=OverallState.model_json_schema(),
        config=ConfigModel.model_json_schema(),
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
                    name="source_code_local",
                    url=AnyUrl("file://../"),
                    framework_config=LangGraphConfig(
                        framework_type="langgraph",
                        graph="sentinel007.app:graph"
                    )
                )
            )
        ],
        env_vars=[EnvVar(name="AZURE_OPENAI_API_KEY", desc="Azure key for the OpenAI service"),
                  EnvVar(name="AZURE_OPENAI_ENDPOINT", desc="Azure endpoint for the OpenAI service"),
                  EnvVar(name="SENDGRID_API_KEY", desc="Sendgrid API key")],
        dependencies=[
            AgentDependency(
                name="mailcomposer",
                ref=AgentRef(name="org.agntcy.intention-analyzer", version="0.0.1", url=AnyUrl("file://intentionanalyzer.json")),
                deployment_option = None,
                env_var_values = None
            ),
            AgentDependency(
                name="email_reviewer",
                ref=AgentRef(name="org.agntcy.prompt-analyzer", version="0.0.1", url=AnyUrl("file://promptanalyzer.json")),
                deployment_option = None,
                env_var_values = None
            ),
           AgentDependency(
                name="email_reviewer",
                ref=AgentRef(name="org.agntcy.judge", version="0.0.1", url=AnyUrl("file://judge.json")),
                deployment_option = None,
                env_var_values = None
            )
        ]
    )
)

with open(f"{Path(__file__).parent}/../../deploy/sentinel007.json", "w") as f:
    f.write(manifest.model_dump_json(
        exclude_unset=True,
        exclude_none=True,
        indent=2
    ))
