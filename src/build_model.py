import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_model():
    csv_path = "data/processed/smartphones_structured_26cols.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist!")
        return
        
    print("Loading structured database...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} phones.")
    
    # Clean duplicates by model_name
    df = df.drop_duplicates(subset=['model_name'], keep='first').reset_index(drop=True)
    print(f"Deduplicated to {len(df)} phones.")
    
    # Map model_name to name to maintain compatibility with app.py
    df['name'] = df['model_name']
    
    # Ensure ratings exists and has no nulls
    if 'ratings' not in df.columns:
        df['ratings'] = 4.2
    df['ratings'] = df['ratings'].fillna(4.2)
    
    # Ensure imgURL exists and has no nulls
    if 'imgURL' not in df.columns:
        df['imgURL'] = ''
    df['imgURL'] = df['imgURL'].fillna('')
    
    # Ensure price exists and has no nulls
    if 'price' not in df.columns:
        df['price'] = 19999.0
    df['price'] = df['price'].fillna(19999.0)
    
    # Check and clean the corpus
    df['corpus'] = df['corpus'].fillna('').astype(str)
    
    # Vectorize corpus
    print("Vectorizing corpus...")
    cv = CountVectorizer(max_features=1000, stop_words='english')
    vectors = cv.fit_transform(df['corpus']).toarray()
    
    # Calculate similarity matrix
    print("Computing cosine similarity matrix...")
    similarity = cosine_similarity(vectors)
    print(f"Similarity matrix shape: {similarity.shape}")
    
    # Create output directory
    os.makedirs("src/model", exist_ok=True)
    
    # Save files
    df_out_path = "src/model/dataframe.pkl"
    similarity_out_path = "src/model/similarity.pkl"
    
    print(f"Saving dataframe to {df_out_path}...")
    with open(df_out_path, 'wb') as f:
        pickle.dump(df, f)
        
    print(f"Saving similarity matrix to {similarity_out_path}...")
    with open(similarity_out_path, 'wb') as f:
        pickle.dump(similarity, f)
        
    print("Model building complete and fully synchronized!")

if __name__ == "__main__":
    build_model()
