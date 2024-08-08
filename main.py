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

intro_message = "Hello! I am the front desk assistant for Zikra InfoTech. How can I assist you today?"
request_name_email_message = "Can I please have your name and email address to assist you better?"

# Function to fetch live stock price
# def get_stock_price(stock_symbol):
#     try:
#         stock = yf.Ticker(stock_symbol)
#         todays_data = stock.history(period='1d')
#         return todays_data['Close'][0]
#     except Exception as e:
#         return str(e)

# Streamlit app
st.title("Chat with Zikra InfoTech Assistant")

if 'started' not in st.session_state or not st.session_state.started:
    # Initialize the conversation
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "assistant",
                "content": intro_message
            }
        ]
    )

    st.session_state.thread_id = thread.id
    st.session_state.assistant_id = 'asst_IyXGpxWwdLrCmhvlmlYURn3K'
    st.session_state.history = [{'role': 'assistant', 'content': intro_message}]
    st.session_state.started = True
    st.experimental_rerun()
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
            # Check if the user has provided their name and email
            if 'name' not in st.session_state or 'email' not in st.session_state:
                if "name" in user_input.lower() and "email" in user_input.lower():
                    st.session_state.name = user_input.split("name is ")[1].split()[0]
                    st.session_state.email = user_input.split("email is")[1].split()[0]
                    response_message = f"Thank you! How can I assist you today, {st.session_state.name}?"
                else:
                    response_message = request_name_email_message
                
                st.session_state.history.append({'role': 'user', 'content': user_input})
                st.session_state.history.append({'role': 'assistant', 'content': response_message})
            
            # elif "stock price" in user_input.lower():
            #     # Extract the stock symbol from the user's input
            #     words = user_input.split()
            #     stock_symbol = words[-1].upper()
            #     stock_price = get_stock_price(stock_symbol)
            #     if isinstance(stock_price, float):
            #         response_message = f"The current price of {stock_symbol} is ${stock_price:.2f}."
            #     else:
            #         response_message = f"Could not retrieve the price for {stock_symbol}. Error: {stock_price}"
                
            #     st.session_state.history.append({'role': 'user', 'content': user_input})
            #     st.session_state.history.append({'role': 'assistant', 'content': response_message})
            else:
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
            
            st.experimental_rerun()
