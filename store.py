import chromadb
import config
import llm

client = chromadb.PersistentClient(path=config.DB_DIR)


def get_collection():
    return client.get_or_create_collection(
        name=config.COLLECTION,
        metadata={"hnsw:space": "cosine"},      # ← 用余弦距离
    )


def reset():
    try:
        client.delete_collection(config.COLLECTION)
    except Exception:
        pass


def add_chunks(doc_name: str, chunks: list[str]) -> int:
    col = get_collection()
    embs = llm.embed(chunks)                     # 调 API 算向量
    col.add(
        ids=[f"{doc_name}::{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embs,
        metadatas=[{"source": doc_name, "idx": i} for i in range(len(chunks))],
    )
    return len(chunks)


def search(query: str, top_k: int = config.TOP_K) -> list[dict]:
    col = get_collection()
    qv = llm.embed([query])[0]
    res = col.query(query_embeddings=[qv], n_results=top_k)
    hits = []
    for i, doc in enumerate(res["documents"][0]):
        hits.append({
            "text": doc,
            "source": res["metadatas"][0][i]["source"],
            "score": round(1 - res["distances"][0][i], 4),   # 距离→相似度
        })
    return hits