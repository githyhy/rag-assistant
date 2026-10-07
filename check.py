"""检索质量自检脚本。

用法：
    python check.py

对每个问题检查 Top-1 命中的文档是否符合预期，
并验证"语料里没有的问题"分数是否明显偏低（防幻觉）。
"""
import store

# (问题, 期望命中的文档)
CASES = [
    ("自动驾驶分为哪几个等级？", "01-自动驾驶分级.md"),
    ("激光雷达和毫米波雷达有什么区别？", "02-感知系统.md"),
    ("BEV 和占用网络解决了什么问题？", "03-传感器融合.md"),
    ("规划为什么要分三层？", "04-预测与规划控制.md"),
    ("RTK 和 IMU 各自的作用是什么？", "05-高精地图与定位.md"),
    ("C-V2X 和 DSRC 的区别是什么？", "06-V2X车路协同.md"),
    ("ASIL 等级是怎么划分的？", "07-功能安全与法规.md"),
    ("什么是数据闭环？", "08-数据闭环.md"),
]

# 语料里没有的内容，分数应当明显偏低
MISS_CASES = [
    "特斯拉 FSD 最新版本号是多少？",
    "比亚迪 2026 年销量是多少？",
]


def main() -> None:
    print("=" * 62)
    print("  检索质量自检")
    print("=" * 62)

    ok = 0
    for q, expect in CASES:
        hits = store.search(q, 3)
        top = hits[0]["source"] if hits else "(无结果)"
        score = hits[0]["score"] if hits else 0.0
        passed = top == expect
        ok += passed
        print(f"{'[PASS]' if passed else '[FAIL]'} {q}")
        print(f"        期望 {expect}")
        print(f"        实际 {top}   (score={score:.3f})")

    print("-" * 62)
    print(f"命中率: {ok}/{len(CASES)}")

    print("\n语料中不存在的问题（分数应明显低于上面的命中项）：")
    for q in MISS_CASES:
        hits = store.search(q, 1)
        if hits:
            print(f"  {hits[0]['score']:.3f}  {q}")
        else:
            print(f"  (无结果)  {q}")
    print("=" * 62)


if __name__ == "__main__":
    main()
