import os
import requests
import urllib.parse
import cloudscraper

from bs4 import BeautifulSoup

"""
BASE_URL：要爬取的网站
STORAGE_PATH：存储图片的路径
HEADERS：请求头
"""
BASE_URL = "https://dogemanga.com"
STORAGE_PATH = "storage"
MANGA_PATH = STORAGE_PATH
os.makedirs(STORAGE_PATH, exist_ok=True)  # 创建存储图片的文件夹
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 "
                  "Safari/537.36",
}


def download_img(chapter_title: str,
                 img_urls: dict,
                 referer: str) -> None:
    """
    下载图片
    :param chapter_title: 章节标题
    :param img_urls: 图片URL集合
    :param referer: 非常重要的一个参数，加在请求头中，否则无法下载图片
    """
    scraper = cloudscraper.create_scraper()
    chapter_path = os.path.join(MANGA_PATH, chapter_title)
    os.makedirs(chapter_path, exist_ok=True)  # 创建章节文件夹

    HEADERS_plus = HEADERS
    HEADERS_plus["referer"] = referer  # 获取新的请求头

    # print("正在下载图片...")
    for img_title, img_url in img_urls.items():
        print("正在下载图片：", img_title)
        img_response = scraper.get(img_url, headers=HEADERS_plus)  # 发送请求
        img_path = os.path.join(chapter_path, f"{img_title}.jpg")
        with open(img_path, "wb") as img_file:
            img_file.write(img_response.content)

    print("章节下载完成：", chapter_title)


def download_chapter(chapter_title: str, chapter_url: str) -> None:
    """
    下载章节
    :param chapter_title: 章节标题
    :param chapter_url: 章节URL
    """
    print("正在下载章节：", chapter_title)
    response = requests.get(chapter_url, headers=HEADERS)  # 发送请求
    soup = BeautifulSoup(response.text, "html.parser")  # 解析HTML内容

    chapter_urls = soup.find_all("img",
                                 class_="site-reader__image")  # 获取每张图片的URL集合

    # print(chapter_urls)
    chapter_img_urls = {}
    for _, img_tag in enumerate(chapter_urls):
        img_title = img_tag.get("alt")
        img_url = img_tag.get("data-page-image-url")
        if img_title and img_url:
            chapter_img_urls[img_title] = img_url
    download_img(chapter_title, chapter_img_urls, chapter_url)


def get_chapters(manga_title: str, manga_url: str) -> dict | None:
    """
    漫画
    :param manga_title: 漫画标题
    :param manga_url: 漫画URL
    """
    print("正在获取章节...")
    response = requests.get(manga_url, headers=HEADERS)  # 发送请求
    soup = BeautifulSoup(response.text, "html.parser")  # 解析HTML内容

    chapter_urls = soup.find_all("a",
                                 class_="vstack gap-1 site-manga-thumbnail__link")  # 获取章节URL集合

    chapter_to_image_urls = {}
    for a_tag in chapter_urls:
        chapter_name = a_tag.find("img").get("alt")
        href_value = a_tag.get("href")
        if chapter_name and href_value:
            chapter_to_image_urls[chapter_name] = href_value

    # 如果章节URL集合不为空，返回章节URL集合
    if chapter_to_image_urls:
        return chapter_to_image_urls
    else:
        print("未找到相关章节，请稍后再试！")  # 未找到章节，可能是IP被拉黑了，或者这个漫画就是没有章节的


def download_manga(manga_title: str, manga_url: str) -> bool:
    """
    下载漫画
    :param manga_title: 漫画标题
    :param manga_url: 漫画URL
    :return: bool
    """
    print("正在下载漫画...")
    global MANGA_PATH
    MANGA_PATH = os.path.join(STORAGE_PATH, manga_title)
    os.makedirs(MANGA_PATH, exist_ok=True)  # 创建漫画文件夹
    chapter_urls = get_chapters(manga_title, manga_url)  # 获取章节URL集合

    if chapter_urls:
        for chapter, url in chapter_urls.items():
            chapter_path = os.path.join(MANGA_PATH, chapter)
            os.makedirs(chapter_path, exist_ok=True)  # 创建章节文件夹
            download_chapter(chapter, url)

    return True


def get_mangas(manga_name) -> dict | None:
    """
    通过漫画名搜索漫画
    :param manga_name: 漫画名
    :return: 搜索结果的URL
    """
    print("正在搜索漫画...")
    encoded_manga_name = urllib.parse.quote(manga_name)  # 对漫画名进行URL编码
    search_url = f"{BASE_URL}/?q={encoded_manga_name}"
    response = requests.get(search_url, headers=HEADERS)  # 发送请求
    soup = BeautifulSoup(response.text, "html.parser")  # 解析HTML内容

    manga_urls = soup.find_all("a",
                               class_="site-card__link")  # 获取搜索结果的URL集合

    # 创建哈希映射
    manga_title_to_url = {}
    for a_tag in manga_urls:
        img_tag = a_tag.find("img")
        if img_tag:
            alt_text = img_tag.get("alt")
            href_value = a_tag.get("href")
            if alt_text and href_value:
                manga_title_to_url[alt_text] = href_value

    # 如果搜索结果不为空，返回搜索结果
    if manga_urls:
        return manga_title_to_url
    else:
        print("未找到相关漫画，请检查漫画名是否正确！")
        return None


if __name__ == "__main__":
    # 测试搜索漫画
    manga_list = get_mangas("")
    print("搜索结果如下：")
    print(manga_list)

    # 测试下载漫画
    manga_name = input("请输入要下载的漫画名称: ")
    download_manga(manga_name, manga_list[manga_name])
