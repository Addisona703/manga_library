import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'manga_db',
}

# 基本配置
BASE_URL = "https://dogemanga.com"
STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage")
MAX_RETRIES = 3
MAX_THREADS = 5

# 请求头配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

# 确保存储目录存在
os.makedirs(STORAGE_PATH, exist_ok=True) 