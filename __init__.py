from util import create_ascii_art


def great():
    print('-' * 35)
    print(create_ascii_art("Manga"))
    print('-' * 35)
    print("欢迎使用漫画爬虫脚本!ʕ•ᴥ•ʔ")
    print("输入 -h 或 --help 查看帮助")


def channel():
    print('|' + "-" * 10)
    print("|1. 爬取漫画")
    print("|2. 查看漫画库")
    print("|quit/q. 退出")
    print('|' + '-' * 10)


def bye():
    print("bye!(◍˃̶ᗜ˂̶◍)✩")


if __name__ == "__main__":
    great()
    channel()
    bye()
