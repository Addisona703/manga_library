# 漫画爬虫项目

## 项目简介
这是一个用于下载漫画的爬虫程序，可以将在线漫画保存到本地。

## 技术栈
- Python 3.x
- MySQL 数据库
- 第三方库：
  - requests: 处理 HTTP 请求
  - BeautifulSoup4: 解析网页内容
  - mysql-connector-python: MySQL数据库操作

## 项目结构
project/\
├── main.py          # 主程序入口，负责调度其他模块\
├── crawler.py       # 爬虫核心逻辑，包括网页解析与下载\
├── sql.py           # 数据库操作模块，负责保存和查询数据\
├── utils.py         # 工具模块，包含通用功能\
└── README.md        # 项目文档，介绍项目使用方法

## 数据库设计

### manga_library 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 自增主键 |
| pdf_path | VARCHAR(255) | PDF存储路径 |
| pdf_name | VARCHAR(255) | 漫画名称 |
| created_at | TIMESTAMP | 创建时间 |

## 示例
运行程序后，输入目标漫画链接：
> https://example.com/manga/123

爬虫会自动开始下载，下载内容保存在 /downloads 目录中。


## 配置说明

在 `config.py` 中可以修改以下配置：

1. 基本配置
   ```python
   # 基本配置
   BASE_URL = "https://dogemanga.com"  # 漫画网站地址
   STORAGE_PATH = "storage"            # 下载文件保存路径
   MAX_RETRIES = 3                     # 最大重试次数
   MAX_THREADS = 5                     # 最大线程数
   ```

2. 请求头配置
   ```python
   HEADERS = {
       "User-Agent": "Mozilla/5.0 ...",  # 从浏览器开发者工具中获取
       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
       "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
       "Accept-Encoding": "gzip, deflate, br",
       "Connection": "keep-alive",
   }
   ```
   - User-Agent 可以从浏览器开发者工具 -> Network 标签页中获取

3. 数据库配置
   ```python
   DB_CONFIG = {
       'host': 'localhost',      # 数据库主机地址
       'port': 3306,            # 数据库端口
       'user': 'root',          # 数据库用户名
       'password': '123456',    # 数据库密码
       'database': 'manga_db',  # 数据库名称
       'charset': 'utf8mb4'     # 字符集
   }
   ```

## 使用方法

### 方式一：命令行使用
1. 克隆项目到本地
   ```bash
   git clone [项目地址]
   ```

2. 创建并激活虚拟环境
   ```bash
   # 创建虚拟环境
   python3 -m venv .venv
   
   # 激活虚拟环境
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 修改配置
   - 按照配置说明修改必要的参数

5. 运行程序
   ```bash
   python main.py
   ```

### 方式二：PyCharm 使用
1. 克隆或下载项目到本地

2. 在 PyCharm 中打开项目
   - 选择 `File` -> `Open` -> 选择项目文件夹

3. 配置 Python 解释器
   - 进入 `File` -> `Settings` -> `Project` -> `Python Interpreter`
   - 点击齿轮图标，选择 `Add`
   - 选择 `Virtual Environment` -> `New environment`
   - 选择 Python 版本，点击 `OK`

4. 安装依赖
   - 打开 PyCharm 终端（View -> Tool Windows -> Terminal）
   - 执行：`pip install -r requirements.txt`

5. 修改配置
   - 按照配置说明修改必要的参数

6. 运行程序
   - 右键点击 `main.py`
   - 选择 `Run 'main'`

## 功能特性
- 支持批量下载漫画章节
- 自动创建目录存储不同漫画
- 断点续传功能
- 数据库记录下载历史

## 注意事项
1. 请合理设置爬虫间隔，避免对目标网站造成压力
2. 下载的内容仅供个人学习使用
3. 确保网络连接稳定

## 常见问题
1. 如遇到 403 错误，请检查 User-Agent 配置
2. 下载失败时会自动重试
3. 数据库路径权限问题，确保有写入权限

## 更新日志
### v1.0.0
- 实现基础爬虫功能
- 添加数据库支持
- 完成文件下载功能

## 贡献指南
欢迎提交 Issue 和 Pull Request 来完善项目

## 许可证
MIT License

---
