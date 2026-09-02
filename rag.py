"""最简版 RAG（检索增强生成）。

教学版先用词频向量 + 余弦相似度做检索，零第三方依赖，方便理解原理。
生产环境会用 embedding 模型（如 text-embedding 系列）+ 向量库（如 ChromaDB）。

原理一句话：把问题变成向量，和每篇文档的向量比相似度，取最像的几段喂给模型。
"""

import glob
import math
import os


def _tokenize(text: str):
    """粗粒度分词：中文按字符切，英文按单词切，去掉标点。"""
    tokens = []
    for ch in text:
        if ch.isalnum() or "\u4e00" <= ch <= "\u9fff":
            tokens.append(ch.lower())
    words = "".join(tokens)
    return words


def _load_docs(directory="knowledge"):
    """读取知识库目录下所有 .md 文件，按段落切分成文档块。"""
    chunks = []
    for path in glob.glob(os.path.join(directory, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # 按空行切段，去掉空段
        for para in content.split("\n\n"):
            para = para.strip()
            if len(para) >= 5:
                chunks.append(para)
    return chunks


def _vector(text: str):
    """把文本变成词频向量（用字典表示：词 -> 出现次数）。"""
    vec = {}
    for word in _tokenize(text):
        vec[word] = vec.get(word, 0) + 1
    return vec


def _cosine(a, b):
    """计算两个向量的余弦相似度，值越大越相似。"""
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[w] * b[w] for w in common)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_knowledge(query: str, top_k: int = 3) -> str:
    """检索知识库，返回最相关的几段文字。"""
    docs = _load_docs()
    if not docs:
        return "知识库为空，请往 knowledge 目录放 .md 文件。"

    q_vec = _vector(query)
    scored = sorted(
        ((_cosine(q_vec, _vector(doc)), doc) for doc in docs),
        key=lambda x: x[0],
        reverse=True
    )
    hits = [doc for score, doc in scored if score > 0][:top_k]
    if not hits:
        return "知识库里没有找到相关内容。"
    return "\n---\n".join(hits)
