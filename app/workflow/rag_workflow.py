from app.models import State
from app.db.vector_store import VectorStore
from app.workflow.reranker import Reranker
from app.config import settings
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from app.workflow.router import LLMClient
import logging

logger = logging.getLogger(__name__)


class RAGWorkflow:
    def __init__(self):
        self.config = settings
        self.vector_store = VectorStore(self.config)
        self.llm = LLMClient(self.config)
        self.reranker = Reranker(self.config)

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
        # if there is a need to analyze the query, use the LLM to analyze the query
        query = {"text": state["question"]}
        return {"query": query}

    def retrieve(self, state: State) -> State:
        query = state["query"]["text"]
        logging.info(f"Retrieving documents for query: {query}")
        retrieved_docs = self.vector_store.semantic_search(query, top_k=10)
        return {"context": retrieved_docs}

    def rerank(self, state: State) -> State:
        if not self.config.enable_reranker:
            return state
        logging.info("Reranking documents")
        query = state["query"]["text"]
        docs = state["context"]
        reranked_docs = self.reranker.rerank(query, docs, top_k=5)
        return {"context": reranked_docs}

    def generate(self, state: State) -> State:
        if not state["context"]:
            return {
                "answer": "Sorry, I couldn't find any relevant information for your query."
            }
        if not self.config.enable_reranker:
            docs_content = "\n\n".join([doc.text for doc in state["context"]])
        else:
            docs_content = "\n\n".join([doc["document"] for doc in state["context"]])
        messages = self.format_prompt(question=state["question"], context=docs_content)
        response = self.llm.chat_completion(messages)
        logging.info(f"Generated response: {response}")
        return {"answer": response["text"]}

    def build(self):
        graph_builder = StateGraph(State).add_sequence(
            [self.analyze_query, self.retrieve, self.rerank, self.generate]
        )
        graph_builder.add_edge(START, "analyze_query")
        memory = MemorySaver()
        return graph_builder.compile(checkpointer=memory)


def build_rag_workflow():
    workflow = RAGWorkflow()
    return workflow.build()
