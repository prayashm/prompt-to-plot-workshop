import pandas as pd
import json
import re
import numpy as np
import random
import os


def parse_price(s):
    if not isinstance(s, str):
        return None
    s = s.strip().lower()
    s = re.sub(r"^[^0-9]+", "", s)  # remove currency codes
    s = s.replace(',', '')
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*(oz|ounce|ounces|grams|g|kg|kilogram|kilograms)", s)
    if not m:
        return None
    price = float(m.group(1))
    qty = float(m.group(2))
    unit = m.group(3)
    if unit.startswith('kg'):
        qty_oz = qty * 35.274
    elif unit.startswith('g') and not unit.startswith('oz'):
        qty_oz = qty / 28.3495
    else:
        qty_oz = qty
    return price / qty_oz


def main():
    df = pd.read_csv('reviews_feb_2023.csv')
    df['price'] = df['est_price'].apply(parse_price)
    for col in ['aroma', 'flavor', 'rating']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['price', 'aroma', 'flavor', 'rating'])

    for col in ['price', 'aroma', 'flavor', 'rating']:
        low = df[col].quantile(0.005)
        high = df[col].quantile(0.995)
        df = df[(df[col] >= low) & (df[col] <= high)]

    df = df.sample(n=min(5000, len(df)), random_state=42)
    records = df[['price', 'aroma', 'flavor', 'rating']].to_dict(orient='records')
    with open('scatter_data.json', 'w') as f:
        json.dump(records, f, separators=(',', ':'))

    size = os.path.getsize('scatter_data.json')
    assert size <= 2 * 1024 * 1024
    print(size)


if __name__ == '__main__':
    main()
