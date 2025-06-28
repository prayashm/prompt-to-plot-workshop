# preprocess.py
import pandas as pd
import numpy as np
import json
import re
import random
import os

def parse_price(est_price_str):
    if pd.isna(est_price_str):
        return None
    
    match = re.search(r'\$(\d+\.?\d*)/(\d+)\s*ounces?', str(est_price_str))
    if match:
        price = float(match.group(1))
        ounces = float(match.group(2))
        return price / ounces
    return None

def main():
    df = pd.read_csv('reviews_feb_2023.csv')
    
    df['price'] = df['est_price'].apply(parse_price)
    df['aroma'] = pd.to_numeric(df['aroma'], errors='coerce')
    df['flavor'] = pd.to_numeric(df['flavor'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    df = df.dropna(subset=['price', 'aroma', 'flavor', 'rating'])
    
    for col in ['price', 'aroma', 'flavor', 'rating']:
        q_low = df[col].quantile(0.005)
        q_high = df[col].quantile(0.995)
        df = df[(df[col] >= q_low) & (df[col] <= q_high)]
    
    if len(df) > 5000:
        random.seed(42)
        df = df.sample(n=5000, random_state=42)
    
    data = df[['price', 'aroma', 'flavor', 'rating']].to_dict('records')
    
    with open('scatter_data.json', 'w') as f:
        json.dump(data, f)
    
    file_size = os.path.getsize('scatter_data.json')
    assert file_size <= 2 * 1024 * 1024, f"File size {file_size} bytes exceeds 2MB limit"
    
    print(f"File size: {file_size} bytes")

if __name__ == "__main__":
    main()