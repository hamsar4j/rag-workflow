from rag_workflow import build_rag_workflow
import streamlit as st
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@st.cache_resource
def get_rag_workflow():
    return build_rag_workflow()


def main():
    st.title("🦙 RAG Chatbot")
    st.markdown("### Ask questions to your knowledge base")

    rag_workflow = get_rag_workflow()
    config = {"configurable": {"thread_id": "abc123"}}

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
        with st.spinner("Searching for answers..."):
            try:
                state = {"question": prompt}
                response = rag_workflow.invoke(state, config=config)
                answer = response["answer"]
            except Exception as e:
                answer = f"Error: {str(e)}"

        # display assistant response
        with st.chat_message("assistant"):
            st.markdown(answer)

        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
