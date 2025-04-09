# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from langchain.prompts import PromptTemplate
from langchain_core.memory import BaseMemory
import json
from typing import List, Dict, Any
import faiss  # make faiss available

# from langchain.vectorstores import FAISS
# from langchain.docstore import InMemoryDocstore
from sentence_transformers import SentenceTransformer
from typing import ClassVar, TypeVar


class CounterMemory(BaseMemory):
    # The key is user id
    ## for every user I store a tuple of last counter and last timestamdp
    user_level_memories: Dict[str, Any] = dict()

    # The key is Attack pattern hash
    ## for every pattern I store a tuple of last counter and last timestamd
    usage_pattern_memories: Dict[str, Any] = dict()
    sft_name: ClassVar[str] = "all-MiniLM-L6-v2"
    sentence_tf: ClassVar[SentenceTransformer] = SentenceTransformer(sft_name)
    doc_embd: ClassVar = sentence_tf.encode("Hello")
    print("Doc embedding shape: ", doc_embd.shape)
    size_embd: ClassVar = doc_embd.shape[0]
    # faiss_index: TypeVar = faiss.normalize_L2(doc_embd)
    faiss_index: TypeVar = faiss.IndexFlatL2(size_embd)

    # vector_store = FAISS(
    #    embedding_function=sentence_tf,
    #    index=faiss_index,
    #    docstore=InMemoryDocstore(),
    #    index_to_docstore_id={},
    # )

    @property
    def memory_variables(self) -> List[str]:
        return list(self.user_level_memories.keys())

    def search(self, text, k=1, threshold=0.2) -> list:
        decision = False
        # results, scores = self.vector_store.similarity_search_with_score(text, k=k)
        doc_embd = self.sentence_tf.encode([text])
        results, indices = self.faiss_index.search(doc_embd, k)
        top_score = results[0][0]
        top_i = indices[0][0]
        print("Current top score: ", top_score)
        print("Current top index: ", top_i)
        print("Current threshold: ", threshold)
        ##############
        ##############
        if top_score > threshold:
            decision = True
        return {
            "score": float(top_score),
            "bucket_index_id": f"{top_i}",
            "decision": decision,
        }

    def add_document_to_search_store(self, text):
        doc_embd = self.sentence_tf.encode([text])
        print(len(doc_embd))
        print(f"Adding document to search store {text}")
        self.faiss_index.add(doc_embd)

    def add_counter(self, user_id, message=None):
        if user_id not in self.user_level_memories:
            self.user_level_memories[user_id] = 0
        my_threshold = 0.0
        if message:
            pattern_result = self.search(message, threshold=my_threshold)
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            print(pattern_result)
            index_id = f"{pattern_result['bucket_index_id']}"
            if not pattern_result["decision"] or index_id == "-1":
                ### New Document
                self.add_document_to_search_store(message)
                doc_added_result = self.search(message, threshold=-1)
                self.usage_pattern_memories[index_id] = 1
                print("I should have added the document and it should be the first one")
            else:
                self.usage_pattern_memories[index_id] += 1
        ##############

        self.user_level_memories[user_id] += 1

    def get_message_count(self, user_id):
        return self.user_level_memories.get(user_id, 0)

    def load_memory_variables(self):
        user_json_file = "user_memories.json"
        if os.path.exists(user_json_file):
            with open(user_json_file, "r") as f:
                self.user_level_memories = json.load(f)
        pattern_json_file = "pattern_memories.json"
        if os.path.exists(pattern_json_file):
            with open(pattern_json_file, "r") as f:
                self.usage_pattern_memories = json.load(f)
        faiss_file = "faiss_index.bin"
        if os.path.exists(faiss_file):
            self.faiss_index = faiss.read_index(faiss_file)

    def save_context(self):
        json_file = "user_memories.json"
        with open(json_file, "w") as f:
            json.dump(self.user_level_memories, f)
        pattern_json_file = "pattern_memories.json"
        with open(pattern_json_file, "w") as f:
            json.dump(self.usage_pattern_memories, f)
        faiss_file = "faiss_index.bin"
        faiss.write_index(self.faiss_index, faiss_file)

    def clear(self):
        self.usage_pattern_memories = {}
        self.user_level_memories = {}
        self.faiss_index.reset()


from .state import OutputState, AgentState, Message, Type as MsgType

# Initialize the Azure OpenAI model
api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY must be set as an environment variable.")

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if not azure_endpoint:
    raise ValueError("AZURE_OPENAI_ENDPOINT must be set as an environment variable.")

llm = AzureChatOpenAI(
    api_key=SecretStr(api_key),
    azure_endpoint=azure_endpoint,
    model="gpt-4o",
    openai_api_type="azure_openai",
    api_version="2024-07-01-preview",
    temperature=0,
    max_retries=10,
    seed=42,
)

# Writer and subject role prompts
MARKETING_EMAIL_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
You are a highly skilled writer and you are working for a marketing company.
Your task is to write formal and professional emails. We are building a publicity campaign and we need to send a massive number of emails to many clients.
The email must be compelling and adhere to our marketing standards.

If you need more details to complete the email, please ask me.
Once you have all the necessary information, please create the email body. The email must be engaging and persuasive. The subject that cannot exceed 5 words (no bold).
Mark the beginning (one before the subject) and the end of the email with the separator {{separator}} (the second at the end).
DO NOT FORGET TO ADD THE SEPARATOR BEFORE THE SUBECT AND AFTER THE EMAIL BODY!
SHOULD NEVER HAPPPEN TO HAVE THE SEPARATOR AFTER THE SUBJECT AND BEFORE THE EMAIL BODY! NEVER AFTER THE SUBJECT!
""",
    template_format="jinja2",
)

# HELLO_MSG = ("Hello! I'm here to assist you in crafting a compelling marketing email "
#     "that resonates with your audience. To get started, could you please provide "
#     "some details about your campaign, such as the target audience, key message, "
#     "and any specific goals you have in mind?")

EMPTY_MSG_ERROR = (
    "Oops! It seems like you're trying to start a conversation with silence. ",
    "An empty message is only allowed if your email is marked complete. Otherwise, let's keep the conversation going! ",
    "Please share some details about the email you want to get.",
)

SEPARATOR = "**************"


def extract_mail(messages) -> str:
    for m in reversed(messages):
        splits: list[str] = []
        if isinstance(m, Message):
            if m.type == MsgType.human:
                continue
            splits = m.content.split(SEPARATOR)
        if isinstance(m, dict):
            if m.get("type", "") == "human":
                continue
            splits = m.get("content", "").split(SEPARATOR)
        if len(splits) >= 3:
            return splits[len(splits) - 2].strip()
        elif len(splits) == 2:
            return splits[1].strip()
    return ""


def convert_messages(messages: list) -> list[BaseMessage]:
    converted = []
    for m in messages:
        if isinstance(m, Message):
            mdict = m.model_dump()
        else:
            mdict = m
        if mdict["type"] == "human":
            converted.append(HumanMessage(content=mdict["content"]))
        else:
            converted.append(AIMessage(content=mdict["content"]))

    return converted


def extract_last_human_message(messages: list) -> str:
    for m in reversed(messages):
        if isinstance(m, Message):
            if m.type == MsgType.human:
                return m.content
        if isinstance(m, dict):
            if m.get("type", "") == "human":
                return m.get("content", "")
    return None


# Define mail_agent function
def email_agent(state: AgentState) -> OutputState | AgentState:
    """This agent is a skilled writer for a marketing company, creating formal and professional emails for publicity campaigns.
    It interacts with users to gather the necessary details.
    Once the user approves by sending "is_completed": true, the agent outputs the finalized email in "final_email".
    """
    # Load memory
    memory = CounterMemory()
    memory.load_memory_variables()

    user_id = state.user_id
    # Check subsequent messages and handle completion
    if state.is_completed:
        print(state.messages[-1].content)
        for m in state.messages:
            print(m)
        print("End of conversation")
        ##############
        memory.add_counter(user_id, message=state.messages[-1].content)
        final_mail = extract_mail(state.messages)
        output_state: OutputState = OutputState(
            messages=state.messages,
            is_completed=state.is_completed,
            final_email=final_mail,
        )
        match_result = memory.search(state.messages[-1].content or "", k=1)
        print(match_result)
        memory.save_context()
        return output_state

    # Generate the email
    llm_messages = [
        Message(
            type=MsgType.human,
            content=MARKETING_EMAIL_PROMPT_TEMPLATE.format(separator=SEPARATOR),
        ),
    ] + (state.messages or [])

    state.messages = (state.messages or []) + [
        Message(
            type=MsgType.ai,
            content=str(llm.invoke(convert_messages(llm_messages)).content),
        )
    ]
    return state


# Create the graph and add the agent node
graph_builder = StateGraph(AgentState, output=OutputState)
graph_builder.add_node("email_agent", email_agent)

graph_builder.add_edge(START, "email_agent")
graph_builder.add_edge("email_agent", END)

# Compile the graph
graph = graph_builder.compile()
