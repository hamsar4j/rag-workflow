import streamlit as st
import requests
import json
from config import config


def query_api(query: str, api_url: str = config.backend_url) -> str:
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
    st.title("🦙 RAG Chatbot")
    st.markdown("### Ask questions to your knowledge base")

    # init chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
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
            st.markdown(answer)

        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
