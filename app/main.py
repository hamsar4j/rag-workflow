import streamlit as st
import requests
import json

backend_url = "http://localhost:8000"


def query_api(query: str, api_url: str = backend_url) -> str:
    try:
        headers = {"Content-Type": "application/json"}
        data = {"query": query}
        response = requests.post(
            f"{api_url}/query", headers=headers, data=json.dumps(data), timeout=30
        )

        response.raise_for_status()

        return response.json()["answer"]

    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the backend: {e}"
    except (KeyError, json.JSONDecodeError) as e:
        return f"Error: Invalid response from the backend: {e}"


def main():
    # Sidebar
    with st.sidebar:
        st.header("🦙 RAG Chatbot")
        st.markdown(
            """
        This is a Retrieval-Augmented Generation (RAG) chatbot that can answer questions
        based on your knowledge base.
        """
        )

        st.markdown(f"**Backend URL:** `{backend_url}`")

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("**Tips:**")
        st.markdown("- Be specific with your questions")
        st.markdown("- Ask about the content in your knowledge base")

    # Main title
    st.title("🦙 RAG Chatbot")
    st.markdown("### Ask questions to your knowledge base")

    # init chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Handle error messages with a different style
            if message["content"].startswith("Error:"):
                st.error(message["content"])
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know?"):
        # add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # get response
        with st.spinner("Searching..."):
            try:
                answer = query_api(prompt)
            except Exception as e:
                answer = f"Error: {str(e)}"

        # display assistant response
        with st.chat_message("assistant"):
            # Handle error messages with a different style
            if answer.startswith("Error:"):
                st.error(answer)
            else:
                st.markdown(answer)

        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
