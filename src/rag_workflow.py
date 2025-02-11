from langgraph.graph import START, StateGraph
from models import State
from vector_store import VectorStore
from langchain import hub
from config import config
from langchain_groq import ChatGroq

def build_rag_workflow():
    # load llm
    llm = ChatGroq(model_name=config.llm_model,api_key=config.groq_api_key)
    # load vector store
    vector_store = VectorStore(config)
    vector_store = vector_store.get_vector_store()
    # load prompt
    prompt = hub.pull("rlm/rag-prompt")

    def retrieve(state: State) -> State:
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    def generate(state: State) -> State:
        docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}

    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    return graph_builder.compile()