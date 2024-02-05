import streamlit as st 
import os
import rapidminer 
import pandas as pd

st.title("📝 Information about Future of Petrochemicals Q & A Chatbot ") 

with st.sidebar:
  st.write("""Document Name : The Future of Petrochemicals \n 
  Document Link: https://iea.blob.core.windows.net/assets/bee4ef3a-8876-4566-98cf-7a130c013805/The_Future_of_Petrochemicals.pdf""")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]
    

# if "chat_engine" not in st.session_state.keys():# Initialize the chat engine
#   index = VectorStoreIndex.from_documents(documents, service_context=service_context)
#   index.storage_context.persist()
#   st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
  

if prompt :=st.text_input("How can i help you today?",placeholder="Your query here"):
  prompt="Provide the citations and elucidate the concepts of"+str(prompt)+"Include detailed information from relevant sections and sub-sections to ensure a comprehensive response."
  st.session_state.messages.append({"role": "user", "content": prompt})
  myinput = pd.DataFrame({'prompt':prompt})


# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            rm = rapidminer.Server("https://myserver.mycompany.com:8080", username="myrmuser")
            training_dataset_sample = rm.run_process("/home/myrmuser/preprocess", inputs=myinput)
            response = training_dataset_sample['new_col']
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)
