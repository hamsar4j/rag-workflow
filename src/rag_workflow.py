from langgraph.graph import START, StateGraph
from models import State, Search
from vector_store import VectorStore
from config import config
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver


class RAGWorkflow:
    def __init__(self):
        self.config = config
        self.vector_store = VectorStore(config).get_vector_store()
        self.llm = init_chat_model(
            model=config.llm_model,
            api_key=config.groq_api_key,
            model_provider=config.model_provider,
        )
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Question: {question}
            Context: {context}
            Answer:
            """
        )

    def analyze_query(self, state: State):
        structured_llm = self.llm.with_structured_output(Search)
        query = structured_llm.invoke(state["question"])
        return {"query": query}

    def retrieve(self, state: State) -> State:
        query = state["query"]
        retrieved_docs = self.vector_store.similarity_search(query["query"])
        return {"context": retrieved_docs}

    def generate(self, state: State) -> State:
        docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
        messages = self.prompt.invoke(
            {"question": state["question"], "context": docs_content}
        )
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
