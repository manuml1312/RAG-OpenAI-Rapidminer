import streamlit as st 
import os
import rapidminer 
import pandas as pd
import json
import requests

st.title("📝 Information about Future of Petrochemicals Q & A Chatbot ") 

with st.sidebar:
  st.write("""Document Name : The Future of Petrochemicals \n 
  Document Link: https://iea.blob.core.windows.net/assets/bee4ef3a-8876-4566-98cf-7a130c013805/The_Future_of_Petrochemicals.pdf""")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]
    


base_url = "http://172.214.107.102/rts/api/v1/services"
endpoint = "/webapp_demo_ff/rag_based_openai_context_prompt"

url = base_url + endpoint
username = 'demo_rapidminer'
password = 'demo_rapidminer'

# if "chat_engine" not in st.session_state.keys():# Initialize the chat engine
#   index = VectorStoreIndex.from_documents(documents, service_context=service_context)
#   index.storage_context.persist()
#   st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
  

if prompt :=st.text_input("How can i help you today?",placeholder="Your query here"):
  prompt="Elucidate the concepts of"+str(prompt)+"Include detailed information from relevant sections and sub-sections to ensure a comprehensive response."
  st.session_state.messages.append({"role": "user", "content": prompt})
  inputs={ "data":[{"prompt":prompt}]}


# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(url, auth=(username, password),json=inputs)
            response_dict = json.loads(response.text)
            # Extracting the content of the "new_col" key
            response2 = response_dict['data'][0]['new_col']
            st.write(response2)
            message = {"role": "assistant", "content": response2}
            st.session_state.messages.append(message)
