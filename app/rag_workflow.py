from models import State, Search
from vector_store import VectorStore
from config import config
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model


class RAGWorkflow:
    def __init__(self):
        self.config = config
        self.vector_store = VectorStore(config)
        self.llm = init_chat_model(
            model=config.llm_model,
            api_key=config.groq_api_key,
        )

    def format_query(self, question: str) -> str:
        return f"""
            Given the user question, reformulate it to be more precise and extract key search terms for a vector search.
            Question: {question}
            """

    def format_prompt(self, question: str, context: str) -> str:
        return f"""
            You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Question: {question}
            Context: {context}
            Answer:
            """

    def analyze_query(self, state: State) -> State:
        structured_llm = self.llm.with_structured_output(Search)
        prompt = self.format_query(state["question"])
        query = structured_llm.invoke(prompt)
        print(f"Analyzed query: {query}")
        return {"query": query}

    def retrieve(self, state: State) -> State:
        query = state["query"]["text"]
        retrieved_docs = self.vector_store.semantic_search(query, top_k=5)
        return {"context": retrieved_docs}

    def generate(self, state: State) -> State:
        if not state["context"]:
            return {
                "answer": "Sorry, I couldn't find any relevant information for your query."
            }
        docs_content = "\n\n".join([doc.text for doc in state["context"]])
        messages = self.format_prompt(question=state["question"], context=docs_content)
        response = self.llm.invoke(messages)
        return {"answer": response.content}

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
