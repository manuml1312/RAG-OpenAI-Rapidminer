import pandas as pd
import openai
import re
from openai import OpenAI



# Cell 3: Set parameters
def rm_main(data):
    client=OpenAI(api_key="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")
    prompt=data['prompt'][0]
    # Use OpenAI GPT for chat completion
    res = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # Choose the appropriate OpenAI GPT engine
        max_tokens=1028,
         messages=[
    			{"role": "system", "content": """Answer the user's query in detail with the provided information.
	             Do not generalize the answer and provide specific terms and technical content as provided in the information.
	            Do not hallucinate,if you dont know the answer say so."""},
    		{"role": "user", "content": str(prompt)}])
    response=dict(dict([dict(res)][0]['choices'][0])['message'])['content']
    rs=pd.DataFrame()
    rs['response']=[response]
    return rs
