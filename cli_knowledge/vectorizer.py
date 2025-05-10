import os
import json
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

def vectorize_snippets(snippets: List[Dict], model_name: str = 'all-MiniLM-L6-v2'):
    """对代码片段进行向量化，返回向量和元数据列表。"""
    model = SentenceTransformer(model_name)
    texts = [s['code'] for s in snippets]
    vectors = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return vectors, snippets

def save_faiss_index(vectors: np.ndarray, meta: List[Dict], index_path: str, meta_path: str):
    """保存向量到 faiss 索引，元数据保存为 json。"""
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, index_path)
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def load_snippets(snippets_path: str) -> List[Dict]:
    with open(snippets_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def search(query: str, index_path: str, meta_path: str, model_name: str = 'all-MiniLM-L6-v2', top_k: int = 5, category: Optional[str] = None):
    """对 query 进行向量化，检索 faiss 索引，返回最相似的代码片段。可选按分类过滤。"""
    model = SentenceTransformer(model_name)
    query_vec = model.encode([query], convert_to_numpy=True)
    index = faiss.read_index(index_path)
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    D, I = index.search(query_vec, top_k * 2)  # 先多取，后面做分类过滤
    results = []
    for idx in I[0]:
        if idx < 0 or idx >= len(meta):
            continue
        item = meta[idx]
        if category:
            if category not in item.get('category', []):
                continue
        results.append(item)
        if len(results) >= top_k:
            break
    return results 