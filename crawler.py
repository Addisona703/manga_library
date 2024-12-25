import os
import random
import mimetypes
import time
import urllib.parse
import requests
import cloudscraper
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# 基本配置
BASE_URL = "https://dogemanga.com"
STORAGE_PATH = "storage"
os.makedirs(STORAGE_PATH, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 "
                  "Safari/537.36",
}
MAX_RETRIES = 3
MAX_THREADS = 5


def log(message: str):
    print(f"[LOG] {message}")


def make_request(url: str, headers: dict, retries: int = MAX_RETRIES) -> requests.Response:
    """
    发送HTTP请求并处理失败重试
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            else:
                log(f"请求失败 [{response.status_code}]: {url}")
        except requests.RequestException as e:
            log(f"请求异常: {e}")
        log(f"重试 {attempt + 1}/{retries} ...")
        time.sleep(random.uniform(1, 3))  # 随机等待 1-3 秒，避免被封 IP
    raise Exception(f"请求失败：{url}")


def get_file_extension_from_url(url):
    """
    从 URL 或响应头中获取文件的扩展名。
    :param url: 图片的 URL
    :return: 文件扩展名（例如 .jpg, .png）
    """
    ext = os.path.splitext(url)[1]  # 从 URL 获取扩展名
    if ext:  # 如果 URL 中存在扩展名
        return ext
    else:
        # 如果 URL 没有扩展名，可以从 MIME 类型推断
        mime_type, _ = mimetypes.guess_type(url)
        if mime_type:
            return mimetypes.guess_extension(mime_type)
    return ".jpg"  # 默认使用 .jpg


def download_single_image(img_title: str, img_url: str, referer: str, chapter_path: str):
    """
    下载单张图片，支持重试机制
    """
    headers = HEADERS.copy()
    headers["referer"] = referer
    file_extension = get_file_extension_from_url(img_url)  # 获取文件扩展名
    img_path = os.path.join(chapter_path, f"{img_title}{file_extension}")

    # 跳过已下载图片
    if os.path.exists(img_path):
        log(f"图片已存在，跳过: {img_title}")
        return

    for attempt in range(MAX_RETRIES):
        try:
            log(f"正在下载图片: {img_title} (尝试 {attempt + 1}/{MAX_RETRIES})")
            response = cloudscraper.create_scraper().get(img_url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(img_path, "wb") as img_file:
                    img_file.write(response.content)
                log(f"图片下载成功: {img_title}")
                return
            else:
                log(f"HTTP 状态码异常: {response.status_code}")
        except Exception as e:
            log(f"图片下载失败: {img_title}, 错误信息: {e}")
        time.sleep(random.uniform(1, 3))
    log(f"图片下载失败，已达最大重试次数: {img_title}")


def download_img(chapter_title: str, img_urls: dict, referer: str, manga_path: str):
    """
    多线程下载章节图片
    """
    chapter_path = os.path.join(manga_path, chapter_title)
    os.makedirs(chapter_path, exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(download_single_image, img_title, img_url, referer, chapter_path)
            for img_title, img_url in img_urls.items()
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log(f"图片下载线程异常: {e}")


def download_chapter(chapter_title: str, chapter_url: str, manga_path: str):
    """
    下载单章节内容
    """
    log(f"正在下载章节: {chapter_title}")
    response = make_request(chapter_url, HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # 获取章节图片 URL 集合
    chapter_urls = soup.find_all("img", class_="site-reader__image")
    if not chapter_urls:
        log(f"未找到章节图片: {chapter_title}")
        return

    chapter_img_urls = {
        img_tag.get("alt"): img_tag.get("data-page-image-url")
        for img_tag in chapter_urls
        if img_tag.get("alt") and img_tag.get("data-page-image-url")
    }

    download_img(chapter_title, chapter_img_urls, chapter_url, manga_path)


def get_chapters(manga_url: str) -> dict:
    """
    获取漫画章节
    """
    log("正在获取章节列表...")
    response = make_request(manga_url, HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # 获取章节URL集合
    chapter_urls = soup.find_all("a", class_="vstack gap-1 site-manga-thumbnail__link")
    if not chapter_urls:
        log("未找到章节信息")
        return {}

    return {
        a_tag.find("img").get("alt"): a_tag.get("href")
        for a_tag in chapter_urls
        if a_tag.find("img") and a_tag.get("href")
    }


def download_manga(manga_title: str, manga_url: str):
    """
    下载漫画
    """
    manga_path = os.path.join(STORAGE_PATH, manga_title)
    os.makedirs(manga_path, exist_ok=True)

    chapters = get_chapters(manga_url)
    if not chapters:
        log("未找到任何章节，可能漫画不存在或网络问题。")
        return

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(download_chapter, chapter_title, chapter_url, manga_path)
            for chapter_title, chapter_url in chapters.items()
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log(f"章节下载线程异常: {e}")

    log(f"漫画下载完成: {manga_title}")


def get_mangas(manga_name: str) -> dict:
    """
    搜索漫画
    """
    log(f"正在搜索漫画: {manga_name}")
    encoded_name = urllib.parse.quote(manga_name)
    search_url = f"{BASE_URL}/?q={encoded_name}"
    response = make_request(search_url, HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # 获取搜索结果
    manga_urls = soup.find_all("a", class_="site-card__link")
    if not manga_urls:
        log("未找到相关漫画，请检查名称是否正确。")
        return {}

    return {
        a_tag.find("img").get("alt"): a_tag.get("href")
        for a_tag in manga_urls
        if a_tag.find("img") and a_tag.get("href")
    }


if __name__ == "__main__":
    manga_name = input("请输入要搜索的漫画名称: ")
    mangas = get_mangas(manga_name)

    if not mangas:
        exit()

    # print("搜索结果如下：")
    # for i, (title, url) in enumerate(mangas.items(), start=1):
    #     print(f"{i}. {title}: {url}")
    #
    # selected_index = int(input("请选择要下载的漫画序号: ")) - 1
    # manga_title, manga_url = list(mangas.items())[selected_index]
    # download_manga(manga_title, manga_url)
