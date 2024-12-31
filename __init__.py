from util import create_ascii_art
from rich.console import Console

MENU_OPTIONS = {
    "1": "爬取漫画",
    "2": "查看漫画库",
    "3": "搜索本地漫画",
    "4": "删除本地漫画",
    "quit/q": "退出"
}

console = Console()

def great() -> None:
    print('-' * 60)
    console.print(create_ascii_art('Manga library'))
    print('-' * 60)
    print("欢迎使用漫画爬虫脚本!ʕ•ᴥ•ʔ\n输入 -h 或 --help 查看帮助")

def channel() -> None:
    print('|' + "-" * 10)
    for key, value in MENU_OPTIONS.items():
        print(f"|{key}. {value}")
    print('|' + '-' * 10)

def bye() -> None:
    print("bye!(◍˃̶ᗜ˂̶◍)✩")

if __name__ == "__main__":
    great()
    channel()
    bye()
