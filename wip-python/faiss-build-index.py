import faiss
import pandas as pd
import sqlite3
import numpy as np
conn = sqlite3.connect("/data/similarity-search/embeddings.sqlite")
df = pd.read_sql_query('SELECT file_id, file_name,  embedding FROM img_embeddings', conn)
df['embedding'] = df['embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32))

dim = df['embedding'][0].shape[0]

index = faiss.IndexFlatIP(dim)

embeddings = np.vstack(df['embedding'].to_numpy())
embeddings.shape
index.add(embeddings)

qid = 4000
query = embeddings[qid][np.newaxis, :]

distances, indices = index.search(query, 5)

df.iloc[np.squeeze(indices)]['file_name'].apply(lambda x: shutil.copy(os.path.join("/data/similarity-search/pictures", x), os.path.join("/data/similarity-search/results", x)))

file_name = df.iloc[qid]['file_name']
os.rename(os.path.join("/data/similarity-search/results", file_name), os.path.join("/data/similarity-search/results", 'query.jpg'))



import shutil
import os
shutil.copy(file_name, os.path.join("/data/similarity-search/pictures", hash_file_name))
