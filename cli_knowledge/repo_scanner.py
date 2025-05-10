import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Optional

def scan_python_files(base_path: str, categories: Optional[List[str]] = None) -> List[Dict]:
    """
    递归扫描 base_path 下所有 .py 文件，抽取函数和类片段。
    返回片段列表，每个片段包含代码、类型、名称、文件路径、类别等元数据。
    """
    results = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        source = f.read()
                        tree = ast.parse(source, filename=file_path)
                        for node in ast.iter_child_nodes(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                start_line = node.lineno
                                end_line = getattr(node, 'end_lineno', None)
                                if not end_line:
                                    # fallback: get last line of body
                                    end_line = node.body[-1].lineno if node.body else node.lineno
                                code_lines = source.splitlines()[start_line-1:end_line]
                                code = '\n'.join(code_lines)
                                results.append({
                                    'type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                                    'name': node.name,
                                    'file_path': file_path,
                                    'category': categories or [],
                                    'code': code
                                })
                    except Exception as e:
                        # 跳过无法解析的文件
                        continue
    return results

def save_snippets(snippets: List[Dict], output_path: str):
    """保存片段到本地 JSON 文件。"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(snippets, f, ensure_ascii=False, indent=2) 