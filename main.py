import os
from sql import *
from crawler import MangaCrawler
from util import *
from __init__ import *

def open_pdf(pdf_name: str, pdf_path: str = "manga_library") -> None:
    print(f"正在打开漫画：{pdf_name}")
    if not os.path.exists(pdf_path):
        print(f"文件不存在：{pdf_path}")
        return

    try:
        if os.name == 'nt':  # Windows
            os.startfile(pdf_path)
        elif os.name == 'posix':  # macOS / Linux
            os.system(f"{'open' if 'darwin' in os.uname().sysname.lower() else 'xdg-open'} '{pdf_path}'")
        print(f"打开文件：{pdf_path}")
    except Exception as e:
        print(f"无法打开文件：{e}")

def get_user_selection(prompt: str, min_value: int, max_value: int) -> int:
    while True:
        user_input = input(prompt)
        if user_input.lower() in ['q', 'quit']:
            return -1
        try:
            selection = int(user_input)
            if min_value <= selection <= max_value:
                return selection
            print(f"请输入一个有效的选项 ({min_value} 到 {max_value})。")
        except ValueError:
            print("无效输入，请输入数字。")

def crawler() -> None:
    manga_crawler = MangaCrawler()
    manga_title = input("请输入要搜索的漫画名称: ")
    if manga_title in ['q', 'quit']:
        return

    mangas_list = manga_crawler.search_manga(manga_title)
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
    manga_crawler.download_manga(manga_title, manga_url)
    create_pdf(manga_title)
    save_pdf_to_database(manga_title)

def manga_library() -> None:
    pdf_files = get_pdf_files_from_database()
    if not pdf_files:
        print("当前漫画库为空，您未下载任何漫画。")
        return

    print("漫画库中的 PDF 文件：")
    for i, (title, path) in enumerate(pdf_files, start=1):
        print(f"{i}. {title}")

    selected_index = get_user_selection("请选择要查看的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(pdf_files))
    if selected_index == -1:
        print("操作已退出。")
        return

    selected_pdf_name, selected_pdf_path = pdf_files[selected_index - 1]
    open_pdf(selected_pdf_name, selected_pdf_path)

def search_manga() -> None:
    while True:
        manga_title = input("请输入要查找的漫画名（输入 'q' 或 'quit' 退出）：").strip()
        if manga_title in ['q', 'quit']:
            print("操作已退出。")
            return

        pdf_files = search_pdf_by_name(manga_title)
        if not pdf_files:
            print("未找到相关漫画，请检查名称是否正确。")
            continue

        print("成功查找到以下漫画：")
        for i, (path, name, _) in enumerate(pdf_files, start=1):
            print(f"{i}. 漫画名: {name}")

        selected_index = get_user_selection("请选择要打开的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(pdf_files))
        if selected_index == -1:
            print("操作已退出。")
            return

        selected_pdf_path, selected_pdf_name, _ = pdf_files[selected_index - 1]
        open_pdf(selected_pdf_name, selected_pdf_path)
        return

def delete_manga() -> None:
    while True:
        manga_title = input("请输入要删除的漫画名（输入 'q' 或 'quit' 退出）：").strip()
        if manga_title in ['q', 'quit']:
            print("操作已退出。")
            return

        pdf_files = search_pdf_by_name(manga_title)
        if not pdf_files:
            print("未找到相关漫画，请检查名称是否正确。")
            continue

        print("成功查找到以下漫画：")
        for i, (path, name, _) in enumerate(pdf_files, start=1):
            print(f"{i}. 漫画名: {name}")

        selected_index = get_user_selection("请选择要删除的漫画序号，或输入 'q' 或 'quit' 退出: ", 1, len(pdf_files))
        if selected_index == -1:
            print("操作已退出。")
            return

        selected_pdf_path, selected_pdf_name, _ = pdf_files[selected_index - 1]
        try:
            delete_pdf_from_database(selected_pdf_name)
            os.remove(selected_pdf_path)
            print(f"成功删除漫画：{selected_pdf_name}")
        except Exception as e:
            print(f"删除失败：{e}")
        return

def main() -> None:
    great()
    menu_options = {'1': crawler, '2': manga_library, '3': search_manga, '4': delete_manga}
    
    while True:
        channel()
        choice = input("请选择一个选项: ")
        if choice in ['q', 'quit']:
            print("退出程序。")
            break
        
        if action := menu_options.get(choice):
            action()
        else:
            print("无效的选项，请重新选择。")
    
    bye()

if __name__ == "__main__":
    main()
