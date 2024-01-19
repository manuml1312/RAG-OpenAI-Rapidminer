# install potentially missing packages
import sys
import subprocess
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

def should_install_requirement(requirement):
    should_install = False
    try:
        pkg_resources.require(requirement)
    except (DistributionNotFound, VersionConflict):
        should_install = True
    return should_install


def install_packages(requirement_list):
    try:
        requirements = [
            requirement
            for requirement in requirement_list
            if should_install_requirement(requirement)
        ]
        if len(requirements) > 0:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *requirements])
        else:
            print("Requirements already satisfied.")

    except Exception as e:
        print(e)

required  = ['cv2','langchain_core','numpy==1.23.2',
             'pandas==1.5.2',
             'openai==0.27.10',
             'datasets==2.8.0',
	      'langchain-openai',
	      'langchain', 'networkx','unstructured[pdf]','faiss-cpu','sentence_transformers','pypdf']

install_packages(required)
  

import pandas as pd

import openai
import requests
from io import BytesIO
from datasets import Dataset
# Cell 1: Import necessary libraries and modules
import os
import re
#from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import CharacterTextSplitter
import faiss
from langchain.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import OpenAI
#
# Function to split text into equal parts
openai_api_key=os.get_environ("OpenAI_Key")
def split_into_equal_parts(text, num_parts=10):
    total_length = len(text)
    part_length = total_length // num_parts
    parts = [text[i:i+part_length] for i in range(0, total_length, part_length)]
    return parts

class Document:
  def __init__(self, page_content, metadata=None):
      self.page_content = page_content
      self.metadata = metadata if metadata is not None else {}

## Cell 2: Load chat data
def load_llm(df):
  print('Start LLM Data Enrichment (OpenAI)...')

  large_text=df['pdf'][0]
  text_parts = split_into_equal_parts(large_text, num_parts=100)
  documents = []
  for idx, part in enumerate(text_parts):
    metadata = {'source': 'https://iea.blob.core.windows.net/assets/bee4ef3a-8876-4566-98cf-7a130c013805/The_Future_of_Petrochemicals.pdf'}
    document = Document(page_content=part, metadata=metadata)
    documents.append(document)

  text_splitter = CharacterTextSplitter(chunk_size=2048, chunk_overlap=256,length_function=len,is_separator_regex=False)
  docs = text_splitter.split_documents(documents)
  embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
  vectorstore_hf = FAISS.from_documents(docs, embeddings)
  return vectorstore_hf

# Cell 3: Set parameters
def rm_main(data,macros):
  prompt = macros['prompt']
  system_prompt="With the help of the retrieved information,answer the user queries accordingly.If you do not know the answer say so.Do not hallucinate and create answers you do not know."

# Cell 4: Prepare data
  df = {'input': [prompt]}
  df = pd.DataFrame(df)
  dataset = Dataset.from_pandas(df)

  print("Application Data (Summary):")
  print(dataset)

  print("First Application Data Examples:")
  print(df.head())
  vectorstore_hf=load_llm(data)
# Cell 5: Define add_target logic
  def add_target(example,vectorstore_hf):
    input_string = prompt
    while re.search('\[\[.*?\]\]', input_string):
        match = re.search('\[\[.*?\]\]', input_string)
        column_name = match.group()
        start = match.start()
        end = match.end()
        input_string = input_string[:start] + example[column_name[0]] + input_string[end:]

    llm = OpenAI(temperature=0,max_tokens=512, openai_api_key=openai_api_key)
    chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore_hf.as_retriever())
    output = chain.invoke({"question": input_string}, return_only_outputs=True)
    return output['answer']


# Cell 6: Apply add_target to the dataset
  result = add_target(dataset,vectorstore_hf)

  outp={'completion':[result]}

  results_df = pd.DataFrame(outp)
  df['new_col'] = results_df['completion']
  return df
