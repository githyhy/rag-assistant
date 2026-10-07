import config
import llm
import store

SYSTEM_PROMPT = """你是一个自动驾驶领域的知识助手。
请严格依据【参考资料】回答用户问题，要求：
1. 只使用参考资料中的信息，不要编造；
2. 如果参考资料不足以回答，明确回答"资料中没有相关内容"；
3. 回答末尾用 [1][2] 的形式标注引用的资料编号。"""


def build_context(hits: list[dict]) -> str:
    return "\n\n".join(
        f"[{i + 1}] 来源：{h['source']}\n{h['text']}" for i, h in enumerate(hits)
    )


def answer(question: str, history: list[dict] | None = None,
           top_k: int = config.TOP_K) -> dict:
    hits = store.search(question, top_k)
    ctx = build_context(hits)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"【参考资料】\n{ctx}\n\n【问题】\n{question}",
    })

    reply = llm.chat(messages)
    return {"answer": reply, "references": hits}
ROUTER_PROMPT = """判断用户问题的类型，只回答一个词：
- retrieve：需要查询知识库才能回答
- chat：日常寒暄，如你好、谢谢
- reject：与自动驾驶无关的问题"""


def route(question: str) -> str:
    out = llm.chat([
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": question},
    ], temperature=0).strip().lower()
    for k in ("retrieve", "chat", "reject"):
        if k in out:
            return k
    return "retrieve"


def answer_with_router(question: str, history=None, top_k=config.TOP_K) -> dict:
    """三个 Agent 分工：意图识别 → 检索 → 生成"""
    intent = route(question)
    if intent == "chat":
        return {"intent": intent, "answer": llm.chat(
            [{"role": "user", "content": question}]), "references": []}
    if intent == "reject":
        return {"intent": intent,
                "answer": "这个问题不在我的知识范围内，我主要回答自动驾驶相关问题。",
                "references": []}
    result = answer(question, history, top_k)
    result["intent"] = intent
    return result