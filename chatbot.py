import streamlit as st
import openai
import os
from query_router import select_tool, get_tool_metadata_by_index
from dotenv import load_dotenv
from llama_index.core.tools import ToolMetadata

from modules.raptor_module.velociraptor import process_or_load_raptor
from llama_index.core import SimpleDirectoryReader


load_dotenv()

client = openai.Client()

def render_chatbot():
    openai_api_key = st.session_state["openai_api_key"]
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam!"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Postavi mi pitanje ovdje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        if(st.button("Resetiraj razgovor")):
            st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam!"}]
        
        try:
            with st.spinner("Odabirem alat..." if st.session_state.debug_mode else "..."):
                selected_tools = select_tool(prompt)

                tool_dict = {tool.index: get_tool_metadata_by_index(tool.index).name for tool in selected_tools}

                if selected_tools and st.session_state.debug_mode:
                    tools_list = "\n".join([f"{i+1}. {tool_dict[tool.index]}" for i, tool in enumerate(selected_tools)])
                    st.success(f"Odabrao sam sljedeće alate:\n{tools_list}")

                if 'raptor' in tool_dict.values():
                    
                    RA = process_or_load_raptor(file_path="./uploaded_files")
                    print("Tree constructed!")
                    answer = RA.answer_question(question=prompt)
                else:
                    answer = get_chatbot_response(prompt)

                if answer:
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.chat_message("assistant").write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
            return


SYSTEM_CONTENT = "You are a helpful assistant for students at the Faculty of Informatics. Respond to user queries and provide information about tools and resources available to students in Croatian language."

def get_chatbot_response(user_prompt, raptor_content):
    openai.api_key = st.session_state["openai_api_key"]
    response = client.chat.completions.create(
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

