import openai

def embedding(text, api_key):
    # OpenAI API Setting
    openai.api_type = "azure"
    openai.api_base = "https://cap-openai-ask-my-underwriter.openai.azure.com/"
    openai.api_version = "2023-09-15-preview"
    openai.api_key = api_key

    emb = openai.Embedding.create(input = [text], engine='text-embedding-ada-002-2')
    emb = [data['embedding'] for data in emb['data']]

    return emb

