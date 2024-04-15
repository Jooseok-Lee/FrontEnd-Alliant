import pandas as pd
import torch
import numpy as np
import faiss

def semantic_search_module(embedding_file, subject_emb, body_emb, pdf_emb, K=1):
    # Get the embedding file
    df = pd.read_csv(embedding_file)
    df['subjects_embeddings'] = df['subjects_embeddings'].apply(lambda x: np.array(x.split(','), dtype=float))
    df['bodys_embeddings'] = df['bodys_embeddings'].apply(lambda x: np.array(x.split(','), dtype=float))
    df['attachments_embeddings'] = df['attachments_embeddings'].apply(lambda x: np.array(x.split(','), dtype=float))

    subjects_vec = np.vstack(df['subjects_embeddings'])
    bodys_vec = np.vstack(df['bodys_embeddings'])
    attachments_vec = np.vstack(df['attachments_embeddings'])

    # Combine indexes into a multi-index structure
    combined_vectors = np.concatenate((subjects_vec, bodys_vec, attachments_vec), axis=1)

    # Parameters for the multi-index
    dimension = combined_vectors.shape[1]  # Combined dimensionality of all modalities (types of text)

    # Create an index
    index = faiss.IndexFlatIP(dimension)  # Assuming Inner Product distance metric

    # Add combined vectors to the index
    index.add(combined_vectors)

    # Query
    combined_query_vector = np.concatenate((np.array(subject_emb), np.array(body_emb), np.array(pdf_emb)), axis=1)

    # Perform search
    D, I = index.search(combined_query_vector, K+1)

    # Result
    search_idx = I[0][1]
    search_subject = df['subject'].iloc[search_idx]
    search_body = df['bodys'].iloc[search_idx]
    search_attachment = df['attachments'].iloc[search_idx]
    search_response = df['bodys_response'].iloc[search_idx]
 
    return search_idx, search_subject, search_body, search_attachment, search_response