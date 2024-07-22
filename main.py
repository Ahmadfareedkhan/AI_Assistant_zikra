import openai
import streamlit as st
import time
import random
import os
from dotenv import load_dotenv
load_dotenv()


# Initialize OpenAI client
api_key = st.secrets.openai.OPENAI_API_KEY
client = openai.Client(api_key=api_key)

# Define the first page
def chat_with_assistant_1():
    st.title("Sales Outreach")

    intro_messages = [
        "Hello! This is {assistant_name} from {business_name}, may I speak with {lead_name}?",
        "Good day! {lead_name}, this is {assistant_name} from {business_name}. How are you today?",
        "Hi {lead_name}, I'm {assistant_name} from {business_name}. Do you have a moment to chat?",
        "Greetings {lead_name}! This is {assistant_name} from {business_name}. Can we talk briefly?",
        "Hello {lead_name}, {assistant_name} here from {business_name}. Is this a good time to speak?"
    ]

    if 'started' not in st.session_state or not st.session_state.started:
        with st.form(key='setup_form'):
            st.header("Setup Chat")
            
            assistant_name = st.text_input("Assistant Name:", "John Doe")
            business_name = st.text_input("Business Name:", "Zikra Infotech LLC")
            lead_name = st.text_input("Lead Name:", "Jane Smith")
            
            submit_button = st.form_submit_button("Start Chat")
            
            if submit_button:
                selected_message = random.choice(intro_messages).format(
                    assistant_name=assistant_name,
                    business_name=business_name,
                    lead_name=lead_name
                )

                # Create a thread with the selected message
                thread = client.beta.threads.create(
                    messages=[
                        {
                            "role": "assistant",
                            "content": selected_message
                        }
                    ]
                )

                st.session_state.thread_id = thread.id
                st.session_state.assistant_id = 'asst_qhlnpeI8umyoDQzQppBB8E7S'
                st.session_state.history = [{'role': 'assistant', 'content': selected_message}]
                st.session_state.started = True
                st.rerun()
    else:
        # Display the chat history
        for message in st.session_state.history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")

        # Input box for user messages
        user_input = st.text_input("Type your message here:")

        if st.button("Send"):
            if user_input:
                message = client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=user_input
                )

                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=st.session_state.assistant_id,
                )

                while True:
                    run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
                    if run.status == 'completed':
                        break
                    time.sleep(0.5)

                messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                current_message = messages.data[0]

                st.session_state.history.append({'role': 'user', 'content': user_input})
                st.session_state.history.append({'role': 'assistant', 'content': current_message.content[0].text.value})
                st.rerun()

# Define the second page
def chat_with_assistant_2():
    st.title("Sales Outreach Followup")

    intro_messages = [
        "Hi, this is {assistant_name} from {business_name}. I'm calling to follow up on your recent interest in {service_name}. Do you have a moment to discuss it further?",
        "Hello, this is {assistant_name} from {business_name}. I noticed you expressed interest in {service_name}, and I wanted to see if you have a few minutes to chat about it.",
        "Good day! This is {assistant_name} from {business_name}. I'm reaching out to follow up on your interest in {service_name}. Do you have a brief moment to talk?",
        "Hi there, this is {assistant_name} with {business_name}. I saw that you were interested in {service_name}, and I wanted to follow up with you. Do you have a couple of minutes to discuss?",
        "Hello, this is {assistant_name} from {business_name}. I'm following up on your inquiry about {service_name}. Do you have some time now to discuss it further?"
    ]

    if 'started' not in st.session_state or not st.session_state.started:
        with st.form(key='setup_form'):
            st.header("Setup Chat")
            
            assistant_name = st.text_input("Assistant Name:", "John Doe")
            business_name = st.text_input("Business Name:", "Zikra Infotech LLC")
            lead_name = st.text_input("Lead Name:", "Jane Smith")
            service_name = st.text_input("Service Name:", "Z360 Management System")
            
            submit_button = st.form_submit_button("Start Chat")
            
            if submit_button:
                selected_message = random.choice(intro_messages).format(
                    assistant_name=assistant_name,
                    business_name=business_name,
                    lead_name=lead_name,
                    service_name=service_name
                )

                # Create a thread with the selected message
                thread = client.beta.threads.create(
                    messages=[
                        {
                            "role": "assistant",
                            "content": selected_message
                        }
                    ]
                )

                st.session_state.thread_id = thread.id
                st.session_state.assistant_id = 'asst_GkETAUo0XlRltW8MYVzdMcha'
                st.session_state.history = [{'role': 'assistant', 'content': selected_message}]
                st.session_state.started = True
                st.rerun()
    else:
        # Display the chat history
        for message in st.session_state.history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")

        # Input box for user messages
        user_input = st.text_input("Type your message here:")

        if st.button("Send"):
            if user_input:
                message = client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=user_input
                )

                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=st.session_state.assistant_id,
                )

                while True:
                    run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
                    if run.status == 'completed':
                        break
                    time.sleep(0.5)

                messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                current_message = messages.data[0]

                st.session_state.history.append({'role': 'user', 'content': user_input})
                st.session_state.history.append({'role': 'assistant', 'content': current_message.content[0].text.value})
                st.rerun()

# Dictionary to map pages to their respective functions
pages = {
    "Assistant: Sales Outreach": chat_with_assistant_1,
    "Assistant: Sales Outreach Followup": chat_with_assistant_2
}

# Sidebar for navigation
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", list(pages.keys()))

# Display the selected page with the respective function
page = pages[selection]
page()
