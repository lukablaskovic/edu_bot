import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.Client()

def chatbot(openai_api_key):

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam! Pitaj me što god želiš 😎"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Postavi mi pitanje ovdje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            answer = get_chatbot_response(prompt, openai_api_key)
            if answer:
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.chat_message("assistant").write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
            return

SYSTEM_CONTENT = "You are a helpful assistant for students at the Faculty of Informatics."

def get_chatbot_response(prompt, openai_api_key):
    openai.api_key = openai_api_key
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= [
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=150,
    )
    return response.choices[0].message.content
