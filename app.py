from pinecone import Pinecone
import os
import pandas as pd
from openai import OpenAI
import re
import streamlit

st.title("📝 Information about Future of Petrochemicals Q & A Chatbot ") 

with st.sidebar:
  st.write("""Document Name : SABIC Materials Q & A Chatbot \n 
  Document Source: Material data scraped from SABIC website""")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]
  


api_key=st.secrets.pinecone_api_key
openai_api_key=st.secrets.openai_api_key

client=OpenAI(api_key=openaiapi_key)
pc = Pinecone(api_key=api_key)
index=pc.Index('genai-petro4')


if prompt :=st.text_input("How can i help you today?",placeholder="Your query here"):
  prompt="Provide the citations and elucidate the concepts of"+str(prompt)+"Include detailed information from relevant sections and sub-sections to ensure a comprehensive response."
  st.session_state.messages.append({"role": "user", "content": prompt})
  myinput = pd.DataFrame({'prompt':prompt})

def create_embeddings(text):
    MODEL = 'text-embedding-ada-002'
    res = client.embeddings.create(input=[text], model=MODEL)
    return dict(dict(res)['data'][0])['embedding']


def index_query(index_name,query,supporting_df,top_k_retrieves=3):
    ids=[]
    ret_text=""
    rets=index_name.query(
        vector=create_embeddings(query),
        top_k=top_k_retrieves,
        include_metadata=True)
    
    for i in range(len(rets['matches'])):
        ids.append(rets['matches'][i]['id'])
    for i in ids:
        ret_text=ret_text + str(supporting_df['text'][[supporting_df.index[supporting_df['ids'] == str(i)]][0][0]])
    return pd.DataFrame({'content':[ret_text]})

supporting_data=pd.read_csv('./supporting_data_website.csv')

ret_text=index_query(index,query,supporting_data,3)



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
