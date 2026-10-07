"""配置。

⚠️ 密钥不要写死在这里！
放到项目根目录的 .env 文件里（该文件已被 .gitignore 排除，不会被提交）。

首次使用：复制 .env.example 为 .env，填入你自己的 key。
"""
import os
from pathlib import Path

_BASE = Path(__file__).resolve().parent


def _load_env(path: Path) -> None:
    """内置的简易 .env 读取器（不依赖任何第三方库）。"""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:      # 已存在的系统环境变量优先
            os.environ[key] = value


# 装了 python-dotenv 就用它，没装就用上面的内置读取器
try:
    from dotenv import load_dotenv            # type: ignore

    load_dotenv(_BASE / ".env")
except ImportError:
    _load_env(_BASE / ".env")


# ===== 模型配置 =====
API_KEY = os.getenv("RAG_API_KEY", "")
BASE_URL = os.getenv("RAG_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
CHAT_MODEL = os.getenv("RAG_CHAT_MODEL", "glm-4-flash")
EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "embedding-3")

if not API_KEY:
    raise RuntimeError(
        "❌ 没有读到 RAG_API_KEY\n"
        f"请创建文件：{_BASE / '.env'}\n"
        "内容写一行：RAG_API_KEY=你的密钥\n"
        "（可以从 .env.example 复制一份改名）"
    )

# ===== 路径（相对项目根目录）=====
DATA_DIR = "data"
DB_DIR = "chroma_db"
COLLECTION = "auto_docs"

# ===== 检索参数（Day 6 要调的就是这几个）=====
CHUNK_SIZE = 400       # 每块字数
CHUNK_OVERLAP = 60     # 相邻块重叠字数
TOP_K = 3              # 检索返回条数
