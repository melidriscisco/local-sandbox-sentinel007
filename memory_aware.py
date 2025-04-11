import os
from langchain_core.memory import BaseMemory
import json
from typing import List, Dict, Any, ClassVar, TypeVar
from sentence_transformers import SentenceTransformer
import faiss  # make faiss available


def seed_index(findex, sentence_tf):
    # Create an array with 40 different text strings
    text_array = [
        "The quick brown fox jumps over the lazy dog",
        "Artificial intelligence is transforming the world",
        "Python is a versatile programming language",
        "Data science involves statistics and machine learning",
        "The weather today is sunny with a chance of rain",
        "Space exploration is a fascinating field of study",
        "Reading books can expand your knowledge and imagination",
        "Music has the power to evoke strong emotions",
        "The internet has revolutionized communication",
        "Machine learning models require large datasets",
        "Traveling allows you to experience new cultures",
        "Healthy eating is essential for a balanced lifestyle",
        "The stock market fluctuates based on various factors",
        "Renewable energy sources are crucial for sustainability",
        "The history of ancient civilizations is intriguing",
        "Sports can teach teamwork and discipline",
        "The human brain is a complex and powerful organ",
        "Technology is advancing at an unprecedented pace",
        "The ocean covers more than 70% of the Earth's surface",
        "Photography captures moments and preserves memories",
        "The study of biology helps us understand living organisms",
        "Programming requires logical thinking and problem-solving",
        "The universe is vast and full of mysteries",
        "Learning new languages can enhance cognitive abilities",
        "The economy is influenced by supply and demand",
        "Art is a form of self-expression and creativity",
        "The importance of mental health cannot be overstated",
        "The automotive industry is shifting towards electric vehicles",
        "Education is the foundation of a prosperous society",
        "The role of government is to serve its citizens",
        "The concept of time travel is popular in science fiction",
        "The healthcare system is vital for public well-being",
        "The principles of physics govern the natural world",
        "The beauty of nature inspires awe and wonder",
        "The rise of social media has changed how we interact",
        "The study of chemistry explains the composition of matter",
        "The importance of cybersecurity is growing in the digital age",
        "The art of cooking combines science and creativity",
        "The global population continues to grow rapidly",
        "The study of mathematics is fundamental to many disciplines",
    ]
    for text in text_array:
        doc_embd = sentence_tf.encode([text])
        findex.add(doc_embd)
    return findex


class MemoryAware(BaseMemory):
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

    @property
    def memory_variables(self) -> List[str]:
        return list(self.user_level_memories.keys())

    def search(self, text, k=1, threshold=1.0) -> list:
        decision = False
        # results, scores = self.vector_store.similarity_search_with_score(text, k=k)
        doc_embd = self.sentence_tf.encode([text])
        results, indices = self.faiss_index.search(doc_embd, k)
        top_score = results[0][0]
        top_i = indices[0][0]
        if top_score <= threshold:
            decision = True
        return {
            "score": float(top_score),
            "bucket_index_id": f"{top_i}",
            "match_found": decision,
        }

    def add_document_to_search_store(self, text):
        doc_embd = self.sentence_tf.encode([text])
        print(len(doc_embd))
        print(f"Adding document to search store {text}")
        self.faiss_index.add(doc_embd)

    def add_counter(self, user_id, message=None):
        if user_id not in self.user_level_memories:
            self.user_level_memories[user_id] = 0
        my_threshold = 1.0
        if message:
            pattern_result = self.search(message, threshold=my_threshold)
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            print(pattern_result)
            index_id = f"{pattern_result['bucket_index_id']}"
            if not pattern_result["match_found"] or index_id == "-1":
                ### New Document
                self.add_document_to_search_store(message)
                doc_added_result = self.search(message, threshold=1.0)
                index_id = f"{doc_added_result['bucket_index_id']}"
                self.usage_pattern_memories[index_id] = 1
                print("I should have added the document and it should be the first one")
            else:
                self.usage_pattern_memories[index_id] += 1

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
