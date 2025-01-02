import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',  # 数据库主机地址
    'port': 3306,  # 数据库端口
    'user': 'root',  # 数据库用户名
    'password': '123456',  # 数据库密码
    'database': 'manga_db',  # 数据库名称
    'charset': 'utf8mb4',  # 字符集
    'use_unicode': True,  # 使用Unicode编码
    'autocommit': True  # 自动提交事务
}

# 基本配置
BASE_URL = "https://dogemanga.com"
MAX_RETRIES = 3
MAX_THREADS = 5

# 获取当前脚本所在的绝对路径
BASE_DIR = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))

# 规范化存储路径
STORAGE_PATH = os.path.normpath(os.path.join(BASE_DIR, "storage"))
OUTPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, "manga_library"))

# 请求头配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 确保必要的目录存在
os.makedirs(STORAGE_PATH, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 图片格式配置
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"] 