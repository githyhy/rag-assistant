"""文档入库脚本。

用法：
    python ingest.py

会先清空旧库，再读取 data/ 下所有 .txt / .md 并写入向量库。

注意：输出只用 ASCII 符号，不用 emoji——
Windows 控制台默认 GBK 编码，emoji 会导致 UnicodeEncodeError。
"""
import config
import loader
import store


def main() -> None:
    print("=" * 56)
    print("  自动驾驶 RAG 知识库 - 文档入库")
    print("=" * 56)
    print(f"  数据目录 : {config.DATA_DIR}")
    print(f"  向量模型 : {config.EMBED_MODEL}")
    print(f"  分块参数 : size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP}")
    print("=" * 56)

    # 1) 清空旧库，避免重复入库
    store.reset()
    print("已清空旧向量库\n")

    # 2) 读取文档
    docs = loader.load_documents()
    if not docs:
        print(f"[X] 没找到文档。请把 .txt / .md 资料放进 {config.DATA_DIR}/ 目录后重试。")
        return

    # 3) 逐篇分块入库
    total_chunks = 0
    failed: list[str] = []

    for d in docs:
        chunks = loader.split_text(d["text"])
        if not chunks:
            print(f"  [!] {d['source']}  内容为空，跳过")
            continue
        try:
            n = store.add_chunks(d["source"], chunks)
            total_chunks += n
            print(f"  [OK] {d['source']}  ->  {n} 块")
        except Exception as e:
            failed.append(d["source"])
            print(f"  [X]  {d['source']}  入库失败: {type(e).__name__}: {e}")

    # 4) 汇总
    print("\n" + "=" * 56)
    print(f"完成: {len(docs) - len(failed)} / {len(docs)} 篇文档, 共入库 {total_chunks} 块")
    if failed:
        print(f"失败文档: {', '.join(failed)}")
    print("=" * 56)

    if total_chunks:
        print("\n下一步: 测试检索")
        print('  python -c "import store; [print(round(h[\'score\'],3), h[\'source\']) for h in store.search(\'自动驾驶分几级\')]"')


if __name__ == "__main__":
    main()
