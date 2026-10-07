"""FastAPI 服务入口。

启动方式：
    双击 start.bat                （推荐，自动建库 + 开浏览器）
    python -m uvicorn main:app --reload --port 8000

页面：
    http://127.0.0.1:8000/        聊天界面
    http://127.0.0.1:8000/docs    接口文档
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import config
import loader
import rag
import store

_BASE = Path(__file__).resolve().parent
_STATIC = _BASE / "static"

app = FastAPI(
    title="自动驾驶知识问答助手",
    description="基于 RAG（检索增强生成）的自动驾驶领域知识问答服务",
    version="1.0.0",
)


# ---------------- 统一响应结构 ----------------
def ok(data=None):
    return {"code": 0, "message": "success", "data": data}


def fail(message: str):
    return {"code": 1, "message": message, "data": None}


def vector_count() -> int:
    try:
        return store.get_collection().count()
    except Exception:
        return 0


# ---------------- 请求体 ----------------
class UploadBody(BaseModel):
    name: str = Field(..., description="文档名，如 感知系统.md")
    text: str = Field(..., description="文档正文")


class SearchBody(BaseModel):
    query: str = Field(..., description="检索问题")
    top_k: int = Field(config.TOP_K, description="返回条数")


class ChatBody(BaseModel):
    question: str = Field(..., description="用户问题")
    history: list[dict] = Field(default_factory=list, description="多轮对话历史")
    top_k: int = Field(config.TOP_K, description="检索条数")
    use_router: bool = Field(True, description="是否启用意图路由")


# ---------------- 页面 ----------------
@app.get("/", include_in_schema=False)
def index():
    page = _STATIC / "index.html"
    if not page.exists():
        raise HTTPException(status_code=500, detail="缺少 static/index.html")
    return FileResponse(page)


# ---------------- 接口 ----------------
@app.get("/api/health", summary="健康检查")
def health():
    return ok({
        "status": "ok",
        "vectors": vector_count(),
        "chat_model": config.CHAT_MODEL,
        "embed_model": config.EMBED_MODEL,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "top_k": config.TOP_K,
    })


@app.post("/api/upload", summary="上传文档并入库")
def upload(body: UploadBody):
    chunks = loader.split_text(body.text)
    if not chunks:
        raise HTTPException(status_code=400, detail="文档内容为空")
    n = store.add_chunks(body.name, chunks)
    return ok({"source": body.name, "chunks": n, "total": vector_count()})


@app.post("/api/search", summary="只检索，不生成")
def search(body: SearchBody):
    return ok({"query": body.query, "hits": store.search(body.query, body.top_k)})


@app.post("/api/chat", summary="RAG 问答（主接口）")
def chat(body: ChatBody):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        if body.use_router:
            result = rag.answer_with_router(body.question, body.history, body.top_k)
        else:
            result = rag.answer(body.question, body.history, body.top_k)
            result["intent"] = "retrieve"
    except Exception as e:
        # 把上游（模型/网络）错误变成结构化响应，前端好处理
        return fail(f"生成失败：{type(e).__name__}: {e}")

    return ok({
        "question": body.question,
        "intent": result.get("intent", "retrieve"),
        "answer": result["answer"],
        "references": [
            {
                "source": h["source"],
                "score": h["score"],
                "text": h["text"][:200],
            }
            for h in result["references"]
        ],
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
