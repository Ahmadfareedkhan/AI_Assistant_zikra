import streamlit as st
import time
from assistant import Assistant
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the Assistant class
ai = Assistant()
ai.create_thread()

# Function to display chat history
def get_chat_history():
    history = ""
    for sender, message in chat_history:
        if sender == "You":
            history += f"<div style='text-align: right;'><strong>{sender}:</strong> {message}</div>"
        else:
            history += f"<div><strong>{sender}:</strong> {message}</div>"
    return history

# Main function for the Streamlit app
def main():
    global chat_history, message_placeholder
    st.title("Live Chat with ZikraInfoTech Frontdesk")

    # Initialize chat history and placeholder for messages
    chat_history = []
    message_placeholder = st.empty()

    # Input field for user message
    user_input = st.text_input("You: ", value="", max_chars=200, key="user_input")

    if st.button("Send"):
        if user_input:
            # Append user's message to the chat history
            chat_history.append(("You", user_input))
            message_placeholder.markdown(get_chat_history(), unsafe_allow_html=True)

            # Send the user's message to the assistant and get the response
            ai.add_message(user_input)
            with st.spinner('Processing...'):
                output, tokens = ai.assistant_api()
                
            # Append assistant's response to the chat history
            chat_history.append(("Assistant", output))
            message_placeholder.markdown(get_chat_history(), unsafe_allow_html=True)

            st.write(f"Tokens Used: {tokens}")

    # Option to end the chat session
    if st.button("End Chat"):
        ai.delete_thread()
        st.write("Chat session ended.")
        st.stop()

if __name__ == "__main__":
    main()
