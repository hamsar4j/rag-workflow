from rag_workflow import build_rag_workflow


def main():
    rag_workflow = build_rag_workflow()
    config = {"configurable": {"thread_id": "abc123"}}

    print("RAG Workflow is ready!")
    print("Type 'quit' or 'q' or 'exit' to stop the program.")
    print("-------------------------------------------")

    while True:
        user_query = input("Enter your query: ")
        if user_query.lower() in ["quit", "exit", "q"]:
            break

        try:
            response = rag_workflow.invoke({"question": user_query}, config=config)
            print(response["answer"])
        except Exception as e:
            print(f"An error occurred: {e}")
        print("-------------------------------------------")


if __name__ == "__main__":
    main()
