# Retrieval Augmented Generation using Rapidminer Studio and AI Hub.

This repository hosts the methods that were used to build a chatbot and deploy it on streamlit using Rapidminer tools and services.There are two approaches that were used.They vary based on the operator and embedding usages which are explained in detail below.

## Approach 1: Text data from pdf chunked and stored in df:
- **Script:** `rapidminer_process1.py`,`app_old.py`
- **Tools**  `Rapidminer Studio`,`Rapidminer AI Hub`,`Streamlit`
- **Operators** `Execute Python`,'Retrieve`
- **Description:**
  - Utilizes Streamlit for a user-friendly chat interface.
  - Employs Langchain library for proces and llm initialization.
  
### Usage
1. Insert the code in rapidminer_process1.py inside the Execute Python operator.
2. Read the textual data from a file, chunk it, store and retrieve it as a dataframe.
3. Input the retrieved dataframe into the python operator.
4. Deploy the process on AI Hub and send and get responses using streamlit platform (app_old.py) to retrieve the generated answer from the model.

## Approach 2: Using Pinecone Vector DB
- **Script:** 'app_pinecone.py`
- **Tools** `Rapidminer Studio`,`Rapidminer AI Hub`,`Pinecone Vector DB`,`Streamlit`
- **Operators** `Execute Python`
- **Description:**
  - Uses Streamlit to create a chat-like interface for user interaction.
  - Employs Langchain library for proces and llm initialization.
  - Uses Pinecone vector db to store and retrieve embeddings.
  - 5x faster and more accurate than Approach 1
Go through the useful_code_snippets.py before to get a clear understanding of the process flow and suitable reasons for why.

### Usage
1. Initialize the llm and chain using the rapidminer_process2.py inside Execute Python Operator.
2. Preprocess the data and store it in Pinecone vector db.
3. I have also stored the text chunks with metadata in a .csv file, from which the text data is extracted based on the top_k retrrieved metadata information.
4. Upload the .csv file on github and configure the path.(more information in useful_code_snippets.py)
5. Deploy the process on AI Hub and send and get responses using streamlit platform (app_old.py) to retrieve the generated answer from the model.

## Dependencies
Ensure you have the necessary dependencies installed by running:
```bash
pip install -r requirements.txt
```

## Configuration
- For the OpenAI API key, create a `secrets.toml` file and store the key as `openai_key` and use as required.

## Contributing
Feel free to contribute to the project by opening issues or submitting pull requests. Your feedback and contributions are highly appreciated.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
