from rag_workflow import build_rag_workflow

if __name__ == "__main__":
    rag_workflow = build_rag_workflow()
    response = rag_workflow.invoke({"question": "What is Task Decomposition?"})
    print(response["answer"])