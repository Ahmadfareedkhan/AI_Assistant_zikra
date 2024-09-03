import streamlit as st
from assistant import Assistant
import time

class StreamlitUI:
    def __init__(self):
        if "assistant" not in st.session_state:
            st.session_state.assistant = Assistant()
            st.session_state.assistant.create_thread()
        self.ai = st.session_state.assistant

    def display_chat_history(self):
        for sender, message in st.session_state.chat_history:
            with st.chat_message(sender.lower()):
                st.write(message)

    def run(self):
        st.set_page_config(page_title="ZikraInfoTech Frontdesk", page_icon="🤖", layout="wide")
        st.title("Live Chat with ZikraInfoTech Frontdesk")

        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        self.display_chat_history()

        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append(("You", user_input))
            
            # Display user message
            with st.chat_message("you"):
                st.write(user_input)

            # Get AI response
            self.ai.add_message(user_input)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.text("Thinking...")
                output, tokens = self.ai.assistant_api()
                message_placeholder.markdown(output)

            # Add AI response to chat history
            st.session_state.chat_history.append(("Assistant", output))

            # Display token usage
            st.sidebar.text(f"Tokens Used: {tokens}")

        # Option to end the chat session
        if st.sidebar.button("End Chat"):
            if "assistant" in st.session_state:
                st.session_state.assistant.delete_thread()
                del st.session_state.assistant
            st.session_state.chat_history = []
            st.sidebar.write("Chat session ended.")
            st.rerun()

if __name__ == "__main__":
    ui = StreamlitUI()
    ui.run()