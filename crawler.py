import os
import random
import mimetypes
import time
import urllib.parse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import cloudscraper
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import BASE_URL, STORAGE_PATH, HEADERS, MAX_RETRIES, MAX_THREADS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='manga_download.log'
)

def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=MAX_RETRIES, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504, 429])
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

def make_request(url: str, headers: dict = None) -> requests.Response:
    headers = headers or HEADERS
    session = create_session()
    
    for _ in range(MAX_RETRIES):
        try:
            response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if _ == MAX_RETRIES - 1:
                logging.error(f"请求失败 {url}: {str(e)}")
                raise Exception(f"请求失败 {url}: {str(e)}")
            time.sleep(random.uniform(2, 5))

def get_file_extension(url: str) -> str:
    ext = os.path.splitext(url)[1]
    if ext: return ext
    mime_type, _ = mimetypes.guess_type(url)
    return mimetypes.guess_extension(mime_type) if mime_type else ".jpg"

def download_image(img_title: str, img_url: str, referer: str, chapter_path: str) -> None:
    img_path = os.path.join(chapter_path, f"{img_title}{get_file_extension(img_url)}")
    if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
        return

    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )

    for _ in range(MAX_RETRIES):
        try:
            response = scraper.get(
                img_url, 
                headers={**HEADERS, "referer": referer}, 
                stream=True, 
                timeout=30
            )
            response.raise_for_status()
            
            if response.status_code == 200:
                temp_path = f"{img_path}.tmp"
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                
                if os.path.getsize(temp_path) > 0:
                    os.replace(temp_path, img_path)
                    return
                os.remove(temp_path)
                raise Exception("下载的文件大小为0")
        except Exception as e:
            if _ == MAX_RETRIES - 1:
                logging.error(f"图片下载失败 {img_title}: {str(e)}")
                raise Exception(f"图片下载失败 {img_title}: {str(e)}")
            time.sleep(random.uniform(2, 5))

def get_mangas(name: str) -> Dict[str, str]:
    response = make_request(f"{BASE_URL}/?q={urllib.parse.quote(name)}")
    soup = BeautifulSoup(response.text, "html.parser")
    return {
        a.find("img").get("alt"): a.get("href")
        for a in soup.find_all("a", class_="site-card__link")
        if a.find("img") and a.get("href")
    }

def get_chapters(manga_url: str) -> Dict[str, str]:
    response = make_request(manga_url)
    soup = BeautifulSoup(response.text, "html.parser")
    return {
        a.find("img").get("alt"): a.get("href")
        for a in soup.find_all("a", class_="vstack gap-1 site-manga-thumbnail__link")
        if a.find("img") and a.get("href")
    }

def download_chapter(chapter_title: str, chapter_url: str, manga_path: str) -> None:
    chapter_path = os.path.join(manga_path, chapter_title)
    os.makedirs(chapter_path, exist_ok=True)

    for _ in range(3):
        try:
            response = make_request(chapter_url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            chapter_imgs = {
                img.get("alt"): img.get("data-page-image-url")
                for img in soup.find_all("img", class_="site-reader__image")
                if img.get("alt") and img.get("data-page-image-url")
            }

            if not chapter_imgs:
                raise Exception(f"未找到章节图片: {chapter_title}")

            with ThreadPoolExecutor(max_workers=min(MAX_THREADS, len(chapter_imgs))) as executor:
                futures = [
                    executor.submit(download_image, title, url, chapter_url, chapter_path)
                    for title, url in chapter_imgs.items()
                ]
                for future in as_completed(futures):
                    future.result()
            return
        except Exception as e:
            if _ == 2:
                logging.error(f"章节下载失败 {chapter_title}: {str(e)}")
                raise
            time.sleep(random.uniform(5, 10))

def download_manga(manga_title: str, manga_url: str) -> None:
    manga_path = os.path.join(STORAGE_PATH, manga_title)
    os.makedirs(manga_path, exist_ok=True)

    chapters = get_chapters(manga_url)
    if not chapters:
        raise Exception("未找到任何章节")

    # 将章节按名称排序
    sorted_chapters = dict(sorted(chapters.items()))
    total_chapters = len(sorted_chapters)
    
    print(f"\n开始下载漫画: {manga_title}，共 {total_chapters} 章")
    with tqdm(total=total_chapters, desc="下载进度", unit="章", ncols=80) as pbar:
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # 使用有序的章节列表创建任务
            future_to_chapter = {
                executor.submit(download_chapter, title, url, manga_path): title
                for title, url in sorted_chapters.items()
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_chapter):
                chapter_title = future_to_chapter[future]
                try:
                    future.result()
                    pbar.update(1)  # 更新进度条
                    pbar.set_description(f"已完成: {chapter_title}")  # 显示当前下载的章节
                except Exception as e:
                    print(f"\n章节 {chapter_title} 下载失败: {e}")

    print(f"\n漫画 {manga_title} 下载完成！")

def main():
    manga_name = input("请输入要搜索的漫画名称: ")
    mangas = get_mangas(manga_name)
    
    if not mangas:
        print("未找到相关漫画")
        return

    print("\n搜索结果:")
    for i, (title, _) in enumerate(mangas.items(), 1):
        print(f"{i}. {title}")

    try:
        idx = int(input("\n请选择要下载的漫画序号: ")) - 1
        manga_title, manga_url = list(mangas.items())[idx]
        download_manga(manga_title, manga_url)
    except (ValueError, IndexError):
        print("输入无效")
    except Exception as e:
        print(f"下载失败: {e}")

if __name__ == "__main__":
    main()
