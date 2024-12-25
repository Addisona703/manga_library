import certifi

from util import *
from __init__ import *
from crawler import *
from sql import save_pdf_to_database


def print_pdf_files(pdf_files: list) -> None:
    """
    打印文件夹中的 PDF 文件列表。
    :param pdf_files: PDF 文件列表
    """
    for i, pdf in enumerate(pdf_files, start=1):
        print(f"{i}. {pdf[0:-4]}")  # 打印文件名，不带扩展名


def get_pdf_files_from_folder(folder_path: str) -> list:
    """
    获取指定文件夹下的所有 PDF 文件。
    :param folder_path: 文件夹路径
    :return: PDF 文件列表
    """
    files = os.listdir(folder_path)  # 获取文件夹下的所有文件
    return [file for file in files if file.lower().endswith('.pdf')]


def open_pdf(pdf_name: str, pdf_path: str = "manga_library") -> None:
    """
    使用系统默认的 PDF 查看器打开文件。
    :param pdf_name: PDF 文件名
    :param pdf_path: PDF 文件路径
    """
    pdf_path = os.path.join(pdf_path, pdf_name)
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


def manga_library() -> None:
    """
    显示漫画库中的所有 PDF 文件。
    """
    folder_path = 'manga_library'
    pdf_files = get_pdf_files_from_folder(folder_path)

    if not pdf_files:
        print("当前漫画库为空，您未下载任何漫画。")
        return

    print("漫画库中的 PDF 文件：")
    for i, title in enumerate(pdf_files, start=1):
        print(f"{i}. {title}")

    selected_index = get_user_selection("请选择要查看的漫画序号: ", 1, len(pdf_files)) - 1
    selected_pdf = pdf_files[selected_index]
    open_pdf(selected_pdf)


def get_user_selection(prompt: str, min_value: int, max_value: int) -> int:
    """
    获取用户的输入并验证有效性。
    :param prompt: 提示信息
    :param min_value: 选择范围的最小值
    :param max_value: 选择范围的最大值
    :return: 用户选择的有效选项
    """
    while True:
        try:
            selection = int(input(prompt))
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

    selected_index = get_user_selection("请选择要下载的漫画序号: ", 1, len(mangas_list)) - 1
    manga_title, manga_url = list(mangas_list.items())[selected_index]

    print(f"开始下载漫画：{manga_title}")
    download_manga(manga_title, manga_url)
    create_pdf(manga_title)
    save_pdf_to_database(manga_title)


def main() -> None:
    """
    主程序，展示欢迎界面并调用相应功能。
    """
    great()

    menu_options = {
        '1': crawler,
        '2': manga_library,
    }

    while True:
        channel()

        choice = input("请选择一个选项: ")

        if choice == 'q' or choice == "quit":
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
    # print(certifi.where())
