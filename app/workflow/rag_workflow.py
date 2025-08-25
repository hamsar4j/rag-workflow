from app.models.models import State, Document, Search
from app.db.vector_db import VectorDB
from app.workflow.reranker import Reranker
from app.core.config import settings
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from app.workflow.router import LLMClient
import logging

logger = logging.getLogger(__name__)


class RAGWorkflow:
    def __init__(self):
        self.config = settings
        self.vector_db = VectorDB(self.config)
        self.llm = LLMClient(self.config)
        self.reranker = Reranker(self.config)

    def format_prompt(self, question: str, context: str) -> str:
        return f"""
        You are a technical assistant. Strictly follow these rules:

        1. Answer ONLY using the provided context
        2. If information is missing, say: "I don't have sufficient information to answer this."
        3. Maximum 10 sentences, be technical and precise
        4. Provide citations with the source URL immediately after the statement in square brackets.
        5. No markdown or formatting.
        6. Return ONLY JSON with "text" field.

        **Question**: {question}

        **Context**: {context}

        Example Response:
        {{ "text": "The Freshmore curriculum is great.[https://www.sutd.edu.sg/education]" }}
        """

    def analyze_query(self, state: State) -> State:
        # if there is a need to analyze the query, use the LLM to analyze the query
        query_text = state["question"]
        query = Search(text=query_text, metadata={}, score=0.0)
        return {**state, "query": query}

    def retrieve(self, state: State) -> State:
        query = state["query"].text
        logger.info(f"Retrieving documents for query: {query}")
        retrieved_docs_from_db = self.vector_db.hybrid_search(query, top_k=10)
        retrieved_docs: list[Document] = [
            Document(text=doc.text, metadata=doc.metadata["metadata"])
            for doc in retrieved_docs_from_db
        ]
        return {**state, "context": retrieved_docs}

    def rerank(self, state: State) -> State:
        if not self.config.enable_reranker:
            return state
        logger.info("Reranking documents")
        query = state["query"].text
        docs = state["context"]
        docs_list = [{"document": doc.text, "metadata": doc.metadata} for doc in docs]

        reranked_docs = self.reranker.rerank(query, docs_list, top_k=5)
        reranked_docs_with_metadata: list[Document] = []
        if reranked_docs and "results" in reranked_docs:
            for item in reranked_docs["results"]:
                if "index" in item:
                    original_index = int(item["index"])
                    if 0 <= original_index < len(docs):
                        original_doc = docs[original_index]
                        reranked_docs_with_metadata.append(original_doc)

        return {**state, "context": reranked_docs_with_metadata}

    def generate(self, state: State) -> State:
        logger.info("Generating response")
        if not state["context"]:
            return {
                **state,
                "answer": "Sorry, I couldn't find any relevant information for your query.",
            }

        docs_content = "\n\n".join(
            [
                f"{doc.text} [source: {doc.metadata.get('source', 'unknown')}]"
                for doc in state["context"]
            ]
        )

        messages = self.format_prompt(question=state["question"], context=docs_content)
        response = self.llm.chat_completion(messages)

        logger.info(f"Generated response: {response}")
        return {
            **state,
            "answer": response["text"] if response else "No response generated",
        }

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
