import mysql.connector
from mysql.connector import Error


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

        # 创建表格（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manga_library (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pdf_path VARCHAR(255),
                pdf_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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


def connect_to_database():
    """
    连接到MySQL数据库。
    :return: 数据库连接对象
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='manga_db'
        )
        if connection.is_connected():
            print("成功连接到数据库")
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
        print("数据库连接已关闭")


if __name__ == "__main__":
    # 测试插入数据
    save_pdf_to_database("芽香小姐無法壓下那份心意")
