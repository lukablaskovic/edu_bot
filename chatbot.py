import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.Client()

def chatbot(openai_api_key):
    st.header("Chatbot Interface")
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    user_input = st.text_input("You: ", key="input")

    if user_input:
        st.session_state['messages'].append({"role": "user", "content": user_input})
        response = get_chatbot_response(user_input, openai_api_key)
        st.session_state['messages'].append({"role": "bot", "content": response})

    for message in st.session_state['messages']:
        if message['role'] == 'user':
            st.write(f"You: {message['content']}")
        else:
            st.write(f"Bot: {message['content']}")

def get_chatbot_response(user_input, openai_api_key):
    openai.api_key = openai_api_key
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.1,
        max_tokens=150,
    )
    return response.choices[0].message.content
