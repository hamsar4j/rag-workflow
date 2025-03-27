from models import State, Search
from vector_store import VectorStore
from config import config
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from router import LLMClient


class RAGWorkflow:
    def __init__(self):
        self.config = config
        self.vector_store = VectorStore(self.config)
        self.llm = LLMClient(self.config)

    def format_query(self, question: str) -> str:
        return f"""
            Given the user question, reformulate it to be more precise and extract key search terms for a vector search.
            Question: {question}
            Return your response as a JSON object that matches this schema:
            Example Response:
            {{
                "text": "reformulated question with key terms",
                "metadata": {{"type": "query_reformulation"}},
                "score": 1.0
            }}
            """

    def format_prompt(self, question: str, context: str) -> str:
        return f"""
            You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Return your response as a JSON object.
            Example Response:
            {{
                "text": "your answer",
            }}
            Question: {question}
            Context: {context}
            Answer:
            """

    def analyze_query(self, state: State) -> State:
        prompt = self.format_query(state["question"])
        query = self.llm.chat_completion(prompt)
        print(f"Analyzed query: {query}")
        return {"query": query}

    def retrieve(self, state: State) -> State:
        query = state["query"]["text"]
        print(f"Retrieving documents for query: {query}")
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
        print(f"Generated response: {response}")
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
