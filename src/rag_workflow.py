from langgraph.graph import START, StateGraph
from models import State, Search
from vector_store import VectorStore
from config import config
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver


def build_rag_workflow():
    # load llm
    llm = init_chat_model(
        model=config.llm_model,
        api_key=config.groq_api_key,
        model_provider=config.model_provider,
    )
    # load vector store
    vector_store = VectorStore(config)
    vector_store = vector_store.get_vector_store()
    # load prompt
    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question} 
        Context: {context} 
        Answer:
        """
    )

    def analyze_query(state: State):
        structured_llm = llm.with_structured_output(Search)
        query = structured_llm.invoke(state["question"])
        return {"query": query}

    def retrieve(state: State) -> State:
        query = state["query"]
        retrieved_docs = vector_store.similarity_search(query["query"])
        return {"context": retrieved_docs}

    def generate(state: State) -> State:
        docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
        messages = prompt.invoke(
            {"question": state["question"], "context": docs_content}
        )
        response = llm.invoke(messages)
        return {"answer": response.content}

    graph_builder = StateGraph(State).add_sequence([analyze_query, retrieve, generate])
    graph_builder.add_edge(START, "analyze_query")
    return graph_builder.compile()
