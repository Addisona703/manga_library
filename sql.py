import mysql.connector
from mysql.connector import Error
from config import db_config

def get_db_config(database_name=None):
    """获取数据库配置，允许自定义数据库名"""
    config = db_config.copy()
    if database_name:
        config['database'] = database_name
    return config

def connect_to_database(database_name=None):
    """连接到MySQL数据库，可选择指定数据库名"""
    try:
        config = get_db_config(database_name)
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def execute_query(query, params=None, fetch=False, database_name=None):
    """执行SQL查询，可指定数据库名"""
    try:
        connection = connect_to_database(database_name)
        if not connection:
            return None
        
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
        if connection and connection.is_connected():
            connection.close()

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
    query = "SELECT pdf_path, pdf_name, created_at FROM manga_library WHERE pdf_name LIKE %s" if fuzzy else "SELECT pdf_path, pdf_name, created_at FROM manga_library WHERE pdf_name = %s"
    params = (f"%{pdf_name}%" if fuzzy else pdf_name,)
    return execute_query(query, params, True) or []

def delete_pdf_from_database(pdf_name: str) -> None:
    """删除PDF记录"""
    execute_query("DELETE FROM manga_library WHERE pdf_name = %s", (pdf_name,))

def init_database(database_name=None):
    """初始化数据库和表，可指定数据库名"""
    db_name = database_name or db_config['database']
    
    # 不指定数据库连接以创建数据库
    execute_query(f"CREATE DATABASE IF NOT EXISTS {db_name}", database_name=None)
    
    # 创建表
    execute_query("""
        CREATE TABLE IF NOT EXISTS manga_library (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pdf_path VARCHAR(255),
            pdf_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, database_name=db_name)

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
