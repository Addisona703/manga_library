import mysql.connector
from mysql.connector import Error, pooling
from config import DB_CONFIG

# 全局连接池
connection_pool = None

def init_pool():
    """初始化连接池"""
    global connection_pool
    if connection_pool is None:
        try:
            pool_config = {
                **DB_CONFIG,
                'pool_name': 'manga_pool',
                'pool_size': 5
            }
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
        except Error as e:
            print(f"连接池初始化失败: {e}")
            raise e

def get_connection():
    """获取数据库连接"""
    global connection_pool
    if connection_pool is None:
        init_pool()
    return connection_pool.get_connection()

def execute_query(query: str, params=None, fetch=False):
    """执行SQL查询"""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        result = cursor.fetchall() if fetch else None
        connection.commit()
        return result
    
    except Error as e:
        print(f"数据库操作失败: {e}")
        if connection:
            connection.rollback()
        return None
    
    finally:
        if connection:
            connection.close()

def init_database():
    """初始化数据库"""
    try:
        # 创建数据库
        temp_conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        temp_conn.close()

        # 创建表
        execute_query("""
            CREATE TABLE IF NOT EXISTS manga_library (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pdf_path VARCHAR(255) NOT NULL,
                pdf_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 初始化连接池
        init_pool()
        print("数据库初始化完成")
    except Error as e:
        print(f"数据库初始化失败: {e}")
        raise e

# 在模块导入时初始化数据库和连接池
try:
    init_database()
except Error as e:
    print(f"数据库初始化失败，请检查配置: {e}")

def save_pdf_to_database(pdf_name: str, pdf_path: str = "manga_library/") -> None:
    """保存PDF到数据库"""
    if execute_query("SELECT COUNT(*) FROM manga_library WHERE pdf_name = %s", (pdf_name,), True)[0][0] > 0:
        print(f"PDF {pdf_name} 已存在。")
        return
    
    execute_query(
        "INSERT INTO manga_library (pdf_path, pdf_name) VALUES (%s, %s)",
        (pdf_path + pdf_name + ".pdf", pdf_name)
    )

def get_pdf_files_from_database() -> list:
    """获取所有PDF文件"""
    result = execute_query("SELECT pdf_name, pdf_path FROM manga_library", fetch=True)
    return result or []

def search_pdf_by_name(pdf_name: str, fuzzy: bool = True) -> list:
    """搜索PDF文件"""
    query = "SELECT pdf_path, pdf_name, created_at FROM manga_library WHERE pdf_name LIKE %s" if fuzzy else "SELECT +pdf_path, pdf_name, created_at FROM manga_library WHERE pdf_name = %s"
    params = (f"%{pdf_name}%" if fuzzy else pdf_name,)
    return execute_query(query, params, True) or []

def delete_pdf_from_database(pdf_name: str) -> None:
    """删除PDF记录"""
    execute_query("DELETE FROM manga_library WHERE pdf_name = %s", (pdf_name,))

def close_pool():
    """关闭连接池"""
    global connection_pool
    if connection_pool:
        try:
            connection_pool.close()
        except Exception:
            pass
        finally:
            connection_pool = None

if __name__ == "__main__":
    # 初始化数据库
    init_database()
    print("数据库初始化完成")
    
    # 测试保存PDF
    save_pdf_to_database("test_manga")
    print("保存PDF测试完成")
    
    # 测试获取所有PDF
    pdfs = get_pdf_files_from_database()
    print(f"当前PDF列表: {pdfs}")
    
    # 测试搜索PDF
    search_results = search_pdf_by_name("test")
    print(f"搜索结果: {search_results}")
    
    # 测试删除PDF
    delete_pdf_from_database("test_manga")
    print("删除PDF测试完成")
    
    # 验证删除结果
    pdfs = get_pdf_files_from_database()
    print(f"删除后的PDF列表: {pdfs}")
