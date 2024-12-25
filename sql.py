import mysql.connector
from mysql.connector import Error

db_data = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'manga_db'
}


def create_database_if_not_exists():
    """
    如果数据库不存在，则创建数据库。
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        cursor = connection.cursor()

        # 创建数据库，如果数据库不存在
        cursor.execute('CREATE DATABASE IF NOT EXISTS manga_db')
        print("数据库 'manga_db' 已创建或已存在。")

        connection.commit()

    except Error as e:
        print(f"创建数据库失败: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def create_table_if_not_exists():
    """
    创建表格 (如果不存在)。
    """
    try:
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库，无法创建表格。")
            return

        cursor = connection.cursor()

        # 创建表格（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manga_library (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pdf_path VARCHAR(255),
                pdf_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("表格 'manga_library' 已创建或已存在。")

        connection.commit()

    except Error as e:
        print(f"创建表格失败: {e}")

    finally:
        close_database_connection(connection)


def save_pdf_to_database(pdf_name: str, pdf_path: str = "manga_library/") -> None:
    """
    将PDF保存到数据库的函数。
    :param pdf_path: PDF文件的路径
    :param pdf_name: 漫画的名称
    """
    full_pdf_path = pdf_path + pdf_name + ".pdf"

    try:
        # 连接数据库
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库，操作终止。")
            return

        cursor = connection.cursor()

        # 检查是否已存在相同 pdf_name
        cursor.execute('''
            SELECT COUNT(*) FROM manga_library WHERE pdf_name = %s
        ''', (pdf_name,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"PDF {pdf_name} 已存在。")
            return

        # 插入PDF文件路径到数据库
        cursor.execute('''
            INSERT INTO manga_library (pdf_path, pdf_name)
            VALUES (%s, %s)
        ''', (full_pdf_path, pdf_name))

        # 提交事务
        connection.commit()
        print(f"PDF路径已成功存储到数据库: {full_pdf_path}")

    except Error as e:
        print(f"数据库操作失败: {e}")
        if connection:
            connection.rollback()  # 回滚操作，避免数据不一致

    finally:
        # 关闭连接
        close_database_connection(connection)


def get_pdf_files_from_database() -> list:
    """
    从数据库中获取保存的所有漫画名称和路径。
    :return: 包含（漫画名称，路径）元组的列表
    """
    try:
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库，操作终止。")
            return []

        cursor = connection.cursor()

        # 查询所有漫画名称和路径
        cursor.execute('SELECT pdf_name, pdf_path FROM manga_library')
        pdf_files = cursor.fetchall()

        return [(name, path) for name, path in pdf_files]

    except Error as e:
        print(f"数据库查询失败: {e}")
        return []

    finally:
        close_database_connection(connection)


def search_pdf_by_name(pdf_name: str, fuzzy: bool = True):
    """
    根据漫画名称查询数据库中的PDF信息，支持精确和模糊查询。
    :param pdf_name: 漫画名称
    :param fuzzy: 是否启用模糊查询（默认关闭）
    :return: 返回匹配的PDF信息列表（包括路径、名称和创建时间）
    """
    try:
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库，操作终止。")
            return []

        cursor = connection.cursor()

        # 根据模糊查询或精确查询的需求构建 SQL 查询
        if fuzzy:
            query = '''
                SELECT pdf_path, pdf_name, created_at FROM manga_library WHERE pdf_name LIKE %s
            '''
            cursor.execute(query, (f"%{pdf_name}%",))
        else:
            query = '''
                SELECT pdf_path, pdf_name, created_at FROM manga_library WHERE pdf_name = %s
            '''
            cursor.execute(query, (pdf_name,))

        results = cursor.fetchall()

        if results:
            # print(f"找到以下匹配的漫画记录：")
            # for i, (path, name, created_at) in enumerate(results, start=1):
            #     print(f"{i}. {name}, 创建时间: {created_at}")
            return results
        else:
            # print(f"没有找到匹配的漫画记录（名称: '{pdf_name}'，模糊查询: {'启用' if fuzzy else '禁用'}）。")
            return []

    except Error as e:
        print(f"数据库查询失败: {e}")
        return []

    finally:
        close_database_connection(connection)


def delete_pdf_from_database(pdf_name: str) -> None:
    """
    从数据库中删除指定的PDF记录。
    :param pdf_name: 漫画名称
    """
    try:
        connection = connect_to_database()
        if not connection:
            print("无法连接到数据库，操作终止。")
            return

        cursor = connection.cursor()

        # 删除指定的 PDF 记录
        cursor.execute('''
            DELETE FROM manga_library WHERE pdf_name = %s
        ''', (pdf_name,))

        connection.commit()
        print(f"成功删除漫画 '{pdf_name}' 的记录。")

    except Error as e:
        print(f"数据库操作失败: {e}")
        if connection:
            connection.rollback()

    finally:
        close_database_connection(connection)


def connect_to_database():
    """
    连接到MySQL数据库。
    :return: 数据库连接对象
    """
    try:
        connection = mysql.connector.connect(**db_data)
        if connection.is_connected():
            # print("成功连接到数据库")
            return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None


def close_database_connection(connection):
    """
    关闭数据库连接。
    :param connection: 数据库连接对象
    """
    if connection and connection.is_connected():
        connection.close()
        # print("数据库连接已关闭")


if __name__ == "__main__":
    # 确保数据库和表格存在
    # create_database_if_not_exists()
    # create_table_if_not_exists()

    # 测试插入数据
    # save_pdf_to_database("芽香小姐無法壓下那份心意")

    # 测试查询数据
    search_pdf_by_name("一拳")
