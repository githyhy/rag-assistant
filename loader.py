"""文档读取与分块。

分块是 RAG 的第一步。这里的策略是 **Markdown 标题感知分块**：
按 # / ## / ### 标题切成小节，并给每块加上
「【文档名 · 章节名】」前缀作为上下文。

好处：即使某块从半句话开始，它的标题关键词也不会丢，
检索时更容易命中（对比实验见 实验记录.md）。
"""
import glob
import os
import re

import config

# 匹配 Markdown 标题行，如 "## 二、融合的三个层次"
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def load_documents(data_dir: str = config.DATA_DIR) -> list[dict]:
    """读取 data/ 下所有 .txt / .md 文件。

    返回 [{"source": 相对路径, "text": 正文}, ...]
    """
    docs: list[dict] = []
    if not os.path.isdir(data_dir):
        return docs

    pattern = os.path.join(data_dir, "**", "*")
    for path in glob.glob(pattern, recursive=True):
        if not os.path.isfile(path):
            continue
        if not path.lower().endswith((".txt", ".md")):
            continue

        # encoding 必须显式指定：Windows 默认 GBK，中文会乱码
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            continue

        docs.append({
            "source": os.path.relpath(path, data_dir),
            "text": text,
        })
    return docs


def _split_long(text: str, chunk_size: int, overlap: int) -> list[str]:
    """把一段长文本按段落聚合成不超过 chunk_size 的块。"""
    paras = [p.strip() for p in text.split("\n") if p.strip()]

    chunks: list[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 1 <= chunk_size:
            buf = (buf + "\n" + p).strip()
            continue

        if buf:
            chunks.append(buf)

        # 单段本身超长（比如一张大表格），只能硬切
        while len(p) > chunk_size:
            chunks.append(p[:chunk_size])
            step = max(1, chunk_size - overlap)
            p = p[step:]
        buf = p

    if buf:
        chunks.append(buf)
    return chunks


def split_text(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[str]:
    """Markdown 标题感知分块。"""
    text = (text or "").strip()
    if not text:
        return []

    doc_title = ""
    sections: list[tuple[str, str]] = []
    cur_head = ""
    cur_lines: list[str] = []

    for raw in text.split("\n"):
        m = _HEADING.match(raw.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1 and not doc_title:
                doc_title = title          # 一级标题作为文档名，不进正文
                continue
            if cur_lines:
                sections.append((cur_head, "\n".join(cur_lines)))
                cur_lines = []
            cur_head = title
            continue
        cur_lines.append(raw)

    if cur_lines:
        sections.append((cur_head, "\n".join(cur_lines)))

    chunks: list[str] = []
    for head, body in sections:
        body = body.strip()
        if not body:
            continue

        if doc_title and head:
            prefix = f"【{doc_title} · {head}】\n"
        elif doc_title:
            prefix = f"【{doc_title}】\n"
        else:
            prefix = ""

        for piece in _split_long(body, chunk_size, overlap):
            chunks.append(prefix + piece)

    return chunks
