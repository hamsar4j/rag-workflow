import streamlit as st
import requests
import json
from app.core.config import settings

backend_url = settings.backend_url


def query_api(query: str, api_url: str = backend_url) -> str:
    """Query the RAG API with the given question."""
    try:
        headers = {"Content-Type": "application/json"}
        data = {"query": query}
        response = requests.post(
            f"{api_url}/query", headers=headers, data=json.dumps(data), timeout=60
        )

        response.raise_for_status()

        result = response.json()
        return result["answer"]

    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again with a more specific question or check your network connection."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the backend service. Please check if the API server is running and accessible."
    except requests.exceptions.HTTPError as e:
        if response.status_code == 500:
            return "Error: Internal server error. Please try again later."
        elif response.status_code == 400:
            return "Error: Bad request. Please check your input and try again."
        else:
            return f"Error: HTTP {response.status_code} - {e}"
    except (KeyError, json.JSONDecodeError):
        return "Error: Invalid response from the backend. The service may be experiencing issues."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"


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
                st.error(message["content"], icon="⚠️")
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know?"):
        # add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # get response
        with st.spinner("Searching knowledge base and generating response..."):
            try:
                answer = query_api(prompt)
            except Exception as e:
                answer = f"Error: {str(e)}"

        # display assistant response
        with st.chat_message("assistant"):
            # Handle error messages with a different style
            if answer.startswith("Error:"):
                st.error(answer, icon="⚠️")
            else:
                st.markdown(answer)

        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
