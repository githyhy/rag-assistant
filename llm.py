from openai import OpenAI
import config

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)


def embed(texts: list[str]) -> list[list[float]]:
    """把文本转成向量"""
    resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def chat(messages: list[dict], temperature: float = 0.3) -> str:
    """调对话模型"""
    resp = client.chat.completions.create(
        model=config.CHAT_MODEL, messages=messages, temperature=temperature
    )
    return resp.choices[0].message.content