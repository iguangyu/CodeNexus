import os
import json
from typing import List

def get_categories(data_dir: str) -> List[str]:
    path = os.path.join(data_dir, "categories.json")
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_categories(data_dir: str, categories: List[str]):
    path = os.path.join(data_dir, "categories.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def add_category(data_dir: str, name: str):
    categories = get_categories(data_dir)
    if name not in categories:
        categories.append(name)
        save_categories(data_dir, categories)

def remove_category(data_dir: str, name: str):
    categories = get_categories(data_dir)
    if name in categories:
        categories.remove(name)
        save_categories(data_dir, categories) 