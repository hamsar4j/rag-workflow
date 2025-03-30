from models import State, Search
from vector_store import VectorStore
from config import config
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from router import LLMClient
import logging

logger = logging.getLogger(__name__)


class RAGWorkflow:
    def __init__(self):
        self.config = config
        self.vector_store = VectorStore(self.config)
        self.llm = LLMClient(self.config)

    def format_query(self, question: str) -> str:
        return f"""
            You are a search optimization expert. Improve this question for vector search by:
            1. Making it more specific and unambiguous
            2. Extracting core technical terms/keyphrases
            3. Preserving the original intent

            **Original Question**: {question}

            **Instructions**:
            - Return ONLY a JSON object with the "text" field containing the optimized query
            - No additional fields or explanations
            - Use technical terminology where appropriate

            Example Response:
            {{ "text": "optimized search query with key terms" }}
            """

    def format_prompt(self, question: str, context: str) -> str:
        return f"""
            You are a technical assistant. Strictly follow these rules:

            1. Answer ONLY using the provided context
            2. If information is missing, say: "I don't have sufficient information to answer this"
            3. Maximum 3 sentences, be technical and precise
            4. No markdown or formatting
            5. Return ONLY JSON with "text" field

            **Question**: {question}

            **Context**: {context}

            Example Response:
            {{ "text": "your concise answer here" }}
            """

    def analyze_query(self, state: State) -> State:
        prompt = self.format_query(state["question"])
        query = self.llm.chat_completion(prompt)
        logging.info(f"Analyzed query: {query}")
        return {"query": query}

    def retrieve(self, state: State) -> State:
        query = state["query"]["text"]
        logging.info(f"Retrieving documents for query: {query}")
        retrieved_docs = self.vector_store.semantic_search(query, top_k=5)
        return {"context": retrieved_docs}

    def generate(self, state: State) -> State:
        if not state["context"]:
            return {
                "answer": "Sorry, I couldn't find any relevant information for your query."
            }
        docs_content = "\n\n".join([doc.text for doc in state["context"]])
        messages = self.format_prompt(question=state["question"], context=docs_content)
        response = self.llm.chat_completion(messages)
        logging.info(f"Generated response: {response}")
        return {"answer": response["text"]}

    def build(self):
        graph_builder = StateGraph(State).add_sequence(
            [self.analyze_query, self.retrieve, self.generate]
        )
        graph_builder.add_edge(START, "analyze_query")
        memory = MemorySaver()
        return graph_builder.compile(checkpointer=memory)


def build_rag_workflow():
    workflow = RAGWorkflow()
    return workflow.build()
