import streamlit as st
import openai
import os
from intent_agent import select_tool, get_tool_metadata_by_index, intent_recognition
from dotenv import load_dotenv
from llama_index.core.tools import ToolMetadata
from streamlit_js_eval import streamlit_js_eval

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

from llama_index.core.node_parser import SentenceSplitter

from modules.raptor_module import RAPTOR


import logging

# Configure logging

openn_ai_client = openai.Client()

def render_chatbot():
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam!"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Postavi mi pitanje ovdje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        velociraptor = RAPTOR(file_path="./uploaded_files/PJS1 - JavaScript osnove.pdf", collection_name="pjs")
        
        intent = intent_recognition(prompt, velociraptor)
        
        print("__________________________INTENT___________________________", intent)
        
        try:
            with st.spinner("Odabirem alat..." if st.session_state.debug_mode else "..."):
                selected_tools = select_tool(prompt)

                tool_dict = {tool.index: get_tool_metadata_by_index(tool.index).name for tool in selected_tools}

                if selected_tools and st.session_state.debug_mode:
                    tools_list = "\n".join([f"{i+1}. {tool_dict[tool.index]}" for i, tool in enumerate(selected_tools)])
                    st.success(f"Odabrao sam sljedeće alate:\n{tools_list}")

                if 'summarizer' in tool_dict.values():

                    

                    response = velociraptor.get_response(prompt)
                    
                    if (response):
                        st.session_state.messages.append({"role": "assistant", "content": str(response)})
                        st.chat_message("assistant").write(str(response))
                    
                
        except Exception as e:
            st.error(f"Greška: {e}")
            return

SYSTEM_CONTENT = "You are a helpful assistant for students at the Faculty of Informatics. Respond to user queries and provide information about tools and resources available to students in Croatian language."

def get_chatbot_response(user_prompt, raptor_content):
    openai.api_key = st.session_state["openai_api_key"]
    response = openn_ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "assistant", "content": raptor_content}, 
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content
