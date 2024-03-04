import os
import pandas as pd
from openai import OpenAI
import re
import streamlit as st
import requests
import json
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
import time

class Document:
  def __init__(self, page_content, metadata=None):
      self.page_content = page_content
      self.metadata = metadata if metadata is not None else {}

def completion(message_text,tokens):
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo-0125", # model = "deployment_name"
      messages = message_text,
      temperature=0.7,
      max_tokens=tokens,
      top_p=0.95,
      frequency_penalty=0,
      presence_penalty=0,
      stop=None
        )
    return completion.choices[0].message.content

class Document:
  def __init__(self, page_content, metadata=None):
      self.page_content = page_content
      self.metadata = metadata if metadata is not None else {}

## Cell 2: Load chat data
def load_vs(text):
  print('Start LLM Data Enrichment (OpenAI)...')
  # encoded_text = text.encode('utf-8')
  total_tokens = round(len(text.split(' '))*1.25)
  total_splits = round(total_tokens / 512)
  if total_splits == 0:
      total_splits=1
      part_length=total_tokens
  else:
     part_length=512

  tokens=[]
  tokens=text.split(' ')

  parts = [tokens[i:i+part_length] for i in range(0, total_splits, part_length)]

  new_parts=[]
  for i in parts:
      j=0
      x=''
      for j in i:
          x+=j+' '
      new_parts.append(x)

  # text_parts = split_into_equal_parts(text, num_parts=25)
  documents = []
  for idx, part in enumerate(new_parts):
    message_text = [{"role":"system","content":"Perform grammatical corrections wherever required for the user's message and come up with a summary of the same"}]
    message_text.append({"role":"user","content":part})
    z=completion(message_text,25)
    metadata = {'source': 'SABIC Website','summary':z}
    document = Document(page_content=part, metadata=metadata)
    documents.append(document)

  text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=64,length_function=len,is_separator_regex=False)
  docs = text_splitter.split_documents(documents)
  embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)#"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")
  vectorstore_hf = FAISS.from_documents(docs, embeddings)
  return vectorstore_hf


@st.cache_data
def processing(text):
    vector_store=load_vs(text)
    vector_store.save_local("vector_store_faiss")
    j=1
    return j

#function to perform vector search on vector store
def search(user_query, vector_store):  
    docs_db = vector_store.similarity_search(user_query, top_k=5)  
    text = ''  
    for i in range(len(docs_db)):  
        text += docs_db[i].page_content + ' '  
    return text 

#function to create streaming effect to chat generation
def response_generator(response):
    comp = response
    if '\n' in comp:
        for line in comp.split('\n\n'):
            words = line.split()
            for i, word in enumerate(words):
                if i > 0:
                    yield " "  # Add space between words
                yield word
                time.sleep(0.05)
            yield "\n"
    else:
        words = comp.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "  # Add space between words
            yield word
            time.sleep(0.05)



def reset_conversation():
  st.session_state.messages=st.session_state.messages = [{"role": "assistant", "content": "Mention your queries!"}]

st.title("📝 SABIC Chatbot \n Explore our products and services.") 

with st.sidebar:
  st.write("""Document Name : SABIC Materials Information Retrieval Chatbot \n 
  Document Source: Material data scraped from SABIC website""")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]

# api_key=st.secrets.pinecone_api_key
openai_api_key=st.secrets.openai_api_key
client=OpenAI(api_key=openai_api_key)

url = "http://20.109.59.175/rts/api/v1/services/newupdated/pinecone_version_streamlit"
username = 'demo_rapidminer'
password = 'demo_rapidminer'


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
      
with st.sidebar:
  st.button("Clear Chat",on_click=reset_conversation)

chat_history = st.session_state.messages

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

df=pd.read_csv('sabic_materials_data.csv')
content=df['context'][0]



# j=0
# while j==0:
j=processing(content)
vector_store = FAISS.load_local("vector_store_faiss",embeddings) 
if vector_store is not None:
    user_query = st.chat_input(placeholder="Your query here")
    if user_query:  
      st.session_state.messages.append({"role": "user", "content": user_query})
      st.chat_message("user").markdown(user_query)
      ret_text=search(user_query,vector_store)
      
      system_prompt=""" Answer the user's query in detail using the provided information. 
		Do not generalize the answer; use specific terms and technical content as provided in the information. 
		Do not hallucinate; if you don't know the answer, state so. Present the output in a professional structured and ordered manne such as point-wise.If the user's query is not related to the provided information,then say the query is out of context.
		Avoid lengthy paragraphs; break the output into small, digestible small paragraphs for ease of comprehension.The information to answer the query is:"""+str(ret_text)
      prompt="My query is: "+str(user_query)+".Provide structured and organized output"
      myinput = {"data":[{"prompt":prompt,"system":system_prompt}]}
    else:
      ret_text=''
else:
  st.stop()
  st.write("Data is processing. Please wait")

if st.session_state.messages[-1]["role"] != "assistant":
    	with st.chat_message("assistant"):
        	with st.spinner("Thinking..."):
			response = requests.post(url,auth=(username, password),json=myinput)
			response_dict = json.loads(response.text)
			s = response_dict['data']
			response2 = s[0]['response']
			st.write_stream(response_generator(response2))
			message = {"role": "assistant", "content": response2}
			st.session_state.messages.append(message)
