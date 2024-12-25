import os
from sql import *
from crawler import *
from util import *
from __init__ import *


def print_pdf_files(pdf_files: list) -> None:
    """
    打印文件夹中的 PDF 文件列表。
    :param pdf_files: PDF 文件列表
    """
    for i, pdf in enumerate(pdf_files, start=1):
        print(f"{i}. {pdf[0:-4]}")  # 打印文件名，不带扩展名


def open_pdf(pdf_name: str, pdf_path: str = "manga_library") -> None:
    """
    使用系统默认的 PDF 查看器打开文件。
    :param pdf_name: PDF 文件名
    :param pdf_path: PDF 文件路径
    """
    print(f"正在打开漫画：{pdf_name}")
    if not os.path.exists(pdf_path):
        print(f"文件不存在：{pdf_path}")
        return

    try:
        # 不同系统的打开方式
        if os.name == 'nt':  # Windows
            os.startfile(pdf_path)
        elif os.name == 'posix':  # macOS / Linux
            if "darwin" in os.uname().sysname.lower():  # macOS
                os.system(f"open '{pdf_path}'")
            else:  # Linux
                os.system(f"xdg-open '{pdf_path}'")
        print(f"打开文件：{pdf_path}")
    except Exception as e:
        print(f"无法打开文件：{e}")


def get_user_selection(prompt: str, min_value: int, max_value: int) -> int:
    """
    获取用户的输入并验证有效性。如果用户输入 'q' 或 'quit'，返回特殊值表示退出。
    :param prompt: 提示信息
    :param min_value: 选择范围的最小值
    :param max_value: 选择范围的最大值
    :return: 用户选择的有效选项，或返回 -1 表示退出
    """
    while True:
        user_input = input(prompt)

        if user_input.lower() in ['q', 'quit']:  # 用户输入 'q' 或 'quit' 时退出
            return -1

        try:
            selection = int(user_input)
            if min_value <= selection <= max_value:
                return selection
            else:
                print(f"请输入一个有效的选项 ({min_value} 到 {max_value})。")
        except ValueError:
            print("无效输入，请输入数字。")


def crawler() -> None:
    """
    漫画爬虫功能，允许用户搜索并下载漫画。
    """
    manga_title = input("请输入要搜索的漫画名称: ")
    if manga_title == 'q' or manga_title == 'quit':
        return
    mangas_list = get_mangas(manga_title)

    if not mangas_list:
        print("未找到相关漫画，请检查名称是否正确。")
        return

    print("搜索结果如下：")
    for i, (title, url) in enumerate(mangas_list.items(), start=1):
        print(f"{i}. {title}: {url}")

    selected_index = get_user_selection("请选择要下载的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(mangas_list))

    if selected_index == -1:
        print("操作已退出。")
        return

    manga_title, manga_url = list(mangas_list.items())[selected_index - 1]

    print(f"开始下载漫画：{manga_title}")
    download_manga(manga_title, manga_url)
    create_pdf(manga_title)
    save_pdf_to_database(manga_title)


def manga_library() -> None:
    """
    显示漫画库中的所有 PDF 文件。
    从数据库中获取漫画名称并显示。
    """
    pdf_files = get_pdf_files_from_database()

    if not pdf_files:
        print("当前漫画库为空，您未下载任何漫画。")
        return

    print("漫画库中的 PDF 文件：")
    for i, (title, path) in enumerate(pdf_files, start=1):
        print(f"{i}. {title}")

    # 让用户选择一个漫画或退出
    selected_index = get_user_selection("请选择要查看的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(pdf_files))

    if selected_index == -1:
        print("操作已退出。")
        return

    selected_pdf_name, selected_pdf_path = pdf_files[selected_index - 1]
    open_pdf(selected_pdf_name, selected_pdf_path)


def search_manga() -> None:
    """
    根据用户输入的漫画名称搜索数据库中的漫画，并提供打开选项。
    """
    while True:
        manga_title = input("请输入要查找的漫画名（输入 'q' 或 'quit' 退出）：").strip()
        if manga_title in ['q', 'quit']:
            print("操作已退出。")
            return

        # 调用数据库搜索函数
        pdf_files = search_pdf_by_name(manga_title)

        if not pdf_files:
            print("未找到相关漫画，请检查名称是否正确。")
        else:
            print("成功查找到以下漫画：")
            for i, (path, name, times) in enumerate(pdf_files, start=1):
                print(f"{i}. 漫画名: {name}")

            selected_index = get_user_selection("请选择要打开的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(pdf_files))

            if selected_index == -1:
                print("操作已退出。")
                return

            selected_pdf_path, selected_pdf_name, data = pdf_files[selected_index - 1]
            open_pdf(selected_pdf_name, selected_pdf_path)
            return


def delete_pdf(selected_pdf_path):
    """
    删除指定的 PDF 文件。
    :param selected_pdf_path: PDF 文件路径
    """
    try:
        os.remove(selected_pdf_path)
        print(f"成功删除文件：{selected_pdf_path}")
    except Exception as e:
        print(f"无法删除文件：{e}")


def delete_manga() -> None:
    """
    根据用户输入的漫画名称删除数据库中的漫画。
    """
    while True:
        manga_title = input("请输入要删除的漫画名（输入 'q' 或 'quit' 退出）：").strip()
        if manga_title in ['q', 'quit']:
            print("操作已退出。")
            return

        # 调用数据库搜索函数
        pdf_files = search_pdf_by_name(manga_title)

        if not pdf_files:
            print("未找到相关漫画，请检查名称是否正确。")
        else:
            print("成功查找到以下漫画：")
            for i, (path, name, times) in enumerate(pdf_files, start=1):
                print(f"{i}. 漫画名: {name}")

            selected_index = get_user_selection("请选择要删除的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(pdf_files))

            if selected_index == -1:
                print("操作已退出。")
                return

            selected_pdf_path, selected_pdf_name, data = pdf_files[selected_index - 1]
            delete_pdf_from_database(selected_pdf_name)
            delete_pdf(selected_pdf_path)
            print(f"成功删除漫画：{selected_pdf_name}")
            return


def main() -> None:
    """
    主程序，展示欢迎界面并调用相应功能。
    """
    great()

    menu_options = {
        '1': crawler,
        '2': manga_library,
        '3': search_manga,
        '4': delete_manga,
    }

    while True:
        channel()

        choice = input("请选择一个选项: ")

        if choice in ['q', 'quit']:
            print("退出程序。")
            break
        else:
            action = menu_options.get(choice)
            if action:
                action()  # 执行对应功能
            else:
                print("无效的选项，请重新选择。")

    bye()


if __name__ == "__main__":
    main()
