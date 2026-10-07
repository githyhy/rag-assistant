import loader
import config


def test_split_text_basic():
    text = "第一段内容。\n第二段内容。\n第三段内容。"
    chunks = loader.split_text(text, chunk_size=20, overlap=0)
    assert len(chunks) >= 1
    assert all(len(c) <= 20 + 10 for c in chunks)


def test_split_text_empty():
    assert loader.split_text("") == []


def test_split_text_long_para():
    text = "啊" * 1000
    chunks = loader.split_text(text, chunk_size=100, overlap=10)
    assert len(chunks) >= 10