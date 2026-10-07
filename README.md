# 自动驾驶知识问答助手（RAG）

> 基于 **RAG（检索增强生成）** 的自动驾驶领域知识问答服务。
> 提问 → 意图识别 → 向量检索 → 拼装 Prompt → 大模型生成 → 带引用溯源返回。

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square)](https://fastapi.tiangolo.com/)
[![Chroma](https://img.shields.io/badge/VectorDB-Chroma-orange?style=flat-square)](https://www.trychroma.com/)

---

## 项目亮点

| 特性 | 说明 |
|------|------|
| **完整 RAG 链路** | 文档解析 → 分块 → 向量化 → 语义检索 → 生成 → 引用溯源 |
| **防幻觉** | System Prompt 强约束，资料中没有的内容明确拒答，答案带 `[1][2]` 引用角标 |
| **Multi-Agent 意图路由** | 意图识别 Agent 先分类（检索 / 寒暄 / 拒答），再分派处理 |
| **标题感知分块** | 按 Markdown 标题切分，每块带 `【文档名 · 章节名】` 前缀防关键词丢失 |
| **内置聊天界面** | 深色科技风 Web UI，可展开查看引用来源与相似度分数 |
| **一键启动** | 双击 `start.bat` 自动检查环境、建库、启动服务并打开浏览器 |
| **单元测试 + 自检脚本** | `pytest` 覆盖分块逻辑，`check.py` 验证检索质量 |

---

## 系统架构

```
                    ┌──────────────────────────────────────┐
   用户提问  ──────▶ │  意图识别 Agent (route)               │
                    └───────────────┬──────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
         [chat]               [retrieve]              [reject]
      直接寒暄回复        向量检索知识库            礼貌拒答
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  向量库 (Chroma)        │
                    │  cosine 相似度 Top-K    │
                    └───────────┬────────────┘
                                │ 命中的文本块
                                ▼
                    ┌────────────────────────┐
                    │  拼装 Prompt            │
                    │  参考资料 + 问题         │
                    └───────────┬────────────┘
                                ▼
                    ┌────────────────────────┐
                    │  大模型生成             │
                    │  带 [1][2] 引用标注     │
                    └───────────┬────────────┘
                                ▼
                     回答 + 引用来源列表
```

### 数据入库流程

```
data/*.md ──▶ loader 解析 ──▶ 标题感知分块 ──▶ Embedding API ──▶ Chroma
               (读取文件)      (每块带章节前缀)     (向量化)       (持久化)
```

---

## 技术栈

| 层次 | 选型 | 说明 |
|------|------|------|
| 语言 | Python 3.11 | |
| Web 框架 | FastAPI + Uvicorn | 自带交互式接口文档 |
| 向量库 | Chroma | 本地持久化，无需独立服务 |
| 对话模型 | 智谱 `glm-4-flash` | OpenAI 兼容接口 |
| 向量模型 | 智谱 `embedding-3` | 2048 维 |
| 前端 | 原生 HTML/CSS/JS | 零构建依赖，单文件 |

---

## 目录结构

```
rag-assistant/
├── data/                    # 知识库语料（8 篇自动驾驶文档）
│   ├── 01-自动驾驶分级.md
│   ├── 02-感知系统.md
│   ├── 03-传感器融合.md
│   ├── 04-预测与规划控制.md
│   ├── 05-高精地图与定位.md
│   ├── 06-V2X车路协同.md
│   ├── 07-功能安全与法规.md
│   └── 08-数据闭环.md
├── static/
│   └── index.html           # 聊天界面
├── tests/
│   └── test_basic.py        # 分块逻辑单元测试
├── chroma_db/               # 向量库（自动生成，已 gitignore）
├── .env                     # 密钥（已 gitignore）
├── .env.example             # 密钥模板
├── config.py                # 配置：模型、密钥、分块参数
├── llm.py                   # 模型调用封装（向量化 / 对话）
├── loader.py                # 文档读取 + 标题感知分块
├── store.py                 # 向量库读写（入库 / 检索）
├── rag.py                   # RAG 主链路 + 意图路由
├── ingest.py                # 建库脚本
├── main.py                  # FastAPI 服务入口
├── check.py                 # 检索质量自检
├── start.bat                # 一键启动
├── requirements.txt
└── 实验记录.md               # 调优实验与踩坑记录
```

---

## 快速开始

### 方式一：一键启动（推荐）

双击 **`start.bat`**，它会自动完成：

1. 检查虚拟环境
2. 检查/安装依赖
3. 检查/建立向量库
4. 启动服务并打开浏览器

### 方式二：手动启动

```powershell
# 1. 安装依赖
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. 配置密钥：复制 .env.example 为 .env，填入你自己的 API Key
copy .env.example .env

# 3. 建立向量库
.\.venv\Scripts\python.exe ingest.py

# 4. 启动服务
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

访问地址：

| 地址 | 用途 |
|------|------|
| http://127.0.0.1:8000 | **聊天界面** |
| http://127.0.0.1:8000/docs | 交互式接口文档 |
| http://127.0.0.1:8000/redoc | 另一种文档样式 |

---

## 接口说明

### `GET /api/health` — 健康检查

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "vectors": 92,
    "chat_model": "glm-4-flash",
    "embed_model": "embedding-3",
    "chunk_size": 400,
    "chunk_overlap": 60,
    "top_k": 3
  }
}
```

### `POST /api/chat` — RAG 问答（主接口）

请求：

```json
{
  "question": "激光雷达和毫米波雷达有什么区别？",
  "history": [],
  "top_k": 3,
  "use_router": true
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "question": "激光雷达和毫米波雷达有什么区别？",
    "intent": "retrieve",
    "answer": "根据资料 [1][2]，两者的主要区别在于……",
    "references": [
      { "source": "02-感知系统.md", "score": 0.525, "text": "……" }
    ]
  }
}
```

### `POST /api/search` — 仅检索，不生成

便于单独调试检索效果，返回命中的文本块与相似度分数。

### `POST /api/upload` — 上传文档并入库

无需重启服务即可扩充知识库。

---

## 核心设计说明

### 1. 为什么用「标题感知分块」

最初的实现按段落长度聚合切块，实测出现问题：
`03-传感器融合.md` 中标题 `### BEV（Bird's Eye View，鸟瞰图）`
被切在上一块末尾，导致含 BEV 内容的块**以半句话开头**，块内不含 "BEV" 一词，检索直接失败。

改为按 Markdown 标题分节，并给每块加上 `【文档名 · 章节名】` 前缀：

```
【传感器融合 · 五、BEV 与占用网络】
近年两个重要趋势：...
```

即使块内容不完整，关键词依然存在于块内，召回显著提升。

### 2. 为什么自己算向量再传给 Chroma

Chroma 默认会从 HuggingFace 下载内置 embedding 模型，国内网络下极不稳定。
本项目改为**调用 Embedding API 算好向量后显式传入**（`embeddings=` 参数），
彻底避开模型下载，同时让向量模型可自由替换。

### 3. 防幻觉策略

- System Prompt 明确要求：**只依据参考资料回答，资料不足时明确说明**
- 回答必须标注引用编号 `[1][2]`
- 前端展示命中的原文片段与相似度分数，便于人工核对

实测效果：

```
Q: 特斯拉 FSD 最新版本号是多少？
A: 资料中没有相关内容 [1][2][3]。
```

### 4. Multi-Agent 意图路由

`rag.route()` 是一个独立的模型角色，只做一件事：把问题分为三类。

| 意图 | 处理 |
|------|------|
| `retrieve` | 走完整 RAG 链路 |
| `chat` | 直接寒暄回复，不检索 |
| `reject` | 礼貌拒答，不浪费检索与生成开销 |

好处是避免"今天天气怎么样"这类无关问题也去查知识库，
减少无意义调用，也避免模型基于无关资料硬答。

### 5. 密钥管理

密钥存放在 `.env`，由 `config.py` 读取，`.env` 已加入 `.gitignore`。
仓库内只提交 `.env.example` 模板。
`config.py` **不含任何硬编码密钥**，缺失时抛出明确错误提示。

---

## 调优实验

详见 [实验记录.md](实验记录.md)。核心结论：

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 入库块数 | 40 | 91 |
| **Top-1 检索命中率** | **7/8** | **8/8** |
| BEV 相关问题 | 命中错误文档（0.419） | 命中正确文档（0.605） |

检索自检结果（`python check.py`）：

```
[PASS] 自动驾驶分为哪几个等级？        -> 01-自动驾驶分级.md      (0.688)
[PASS] 激光雷达和毫米波雷达有什么区别？  -> 02-感知系统.md          (0.525)
[PASS] BEV 和占用网络解决了什么问题？    -> 03-传感器融合.md        (0.605)
[PASS] 规划为什么要分三层？             -> 04-预测与规划控制.md    (0.651)
[PASS] RTK 和 IMU 各自的作用是什么？    -> 05-高精地图与定位.md    (0.594)
[PASS] C-V2X 和 DSRC 的区别是什么？     -> 06-V2X车路协同.md       (0.637)
[PASS] ASIL 等级是怎么划分的？          -> 07-功能安全与法规.md    (0.638)
[PASS] 什么是数据闭环？                 -> 08-数据闭环.md          (0.578)
------------------------------------------------------------
命中率: 8/8

语料中不存在的问题（分数应明显偏低）：
  0.421  特斯拉 FSD 最新版本号是多少？
  0.316  比亚迪 2026 年销量是多少？
```

---

## 测试

```powershell
# 单元测试（分块逻辑）
.\.venv\Scripts\python.exe -m pytest tests/ -v

# 检索质量自检
.\.venv\Scripts\python.exe check.py
```

---

## 常见问题

<details>
<summary><b>Windows 控制台报 UnicodeEncodeError</b></summary>

控制台默认 GBK 编码，无法输出 emoji。
脚本中一律使用 ASCII 标记（`[OK]` / `[X]`）代替。
</details>

<details>
<summary><b>中文读取乱码</b></summary>

`open()` 必须显式指定 `encoding="utf-8"`，否则 Windows 默认用 GBK。
</details>

<details>
<summary><b>端口被占用（Errno 10048）</b></summary>

先停掉已在运行的服务（原终端按 `Ctrl+C`），或改用其他端口：
`--port 8001`
</details>

<details>
<summary><b>Chroma 卡在下载模型</b></summary>

本项目通过显式传入 `embeddings=` 规避，不会触发模型下载。
若仍卡住，检查是否误用了 `collection.query(query_texts=...)`。
</details>

<details>
<summary><b>双击 start.bat 闪一下就没</b></summary>

批处理文件必须以 **ASCII 或 GBK 编码**保存，且使用 **CRLF** 换行。
保存为 UTF-8 会导致 cmd 按字节偏移解析错乱。
</details>

---

## 后续优化方向

- [ ] 支持 PDF / Word / Excel 文档解析
- [ ] 引入 **Rerank 重排序** 提升 Top-K 精度
- [ ] 混合检索（BM25 + 向量）改善专有名词召回
- [ ] 流式输出（SSE），提升长回答体验
- [ ] 会话持久化与多会话管理
- [ ] Docker 容器化部署

---

## 说明

知识库语料为自行整理撰写的自动驾驶科普文档，参考资料为公开的行业标准与法规信息。
本项目为个人学习实践作品。
