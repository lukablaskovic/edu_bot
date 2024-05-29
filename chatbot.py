import streamlit as st
import openai
import os
from query_router import select_tool, get_tool_metadata_by_index
from dotenv import load_dotenv
from llama_index.core.tools import ToolMetadata



load_dotenv()

client = openai.Client()

def chatbot(openai_api_key: str):

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam! Pitaj me što god želiš 😎"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Postavi mi pitanje ovdje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            with st.spinner("Odabirem alat..." if st.session_state.debug_mode else "..."):
                selected_tool = select_tool(prompt)
                if selected_tool and st.session_state.debug_mode == True:
                    if len(selected_tool) == 1:
                        tool_metadata = get_tool_metadata_by_index(selected_tool[0].index)
                        st.success(f"Odabrao sam alat: {tool_metadata.name}")
                    else:
                        tool_names = [get_tool_metadata_by_index(tool.index).name for tool in selected_tool]
                        tools_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(tool_names)])
                        st.success(f"Odabrao sam sljedeće alate:\n{tools_list}")


            answer = get_chatbot_response(prompt, openai_api_key)
            if answer:
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.chat_message("assistant").write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
            return

SYSTEM_CONTENT = "You are a helpful assistant for students at the Faculty of Informatics. Respond to user queries and provide information about tools and resources available to students in Croatian language."

def get_chatbot_response(prompt: str, openai_api_key: str):
    openai.api_key = openai_api_key
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=150,
    )
    return response.choices[0].message.content

