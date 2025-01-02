import os
import random
import mimetypes
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

import cloudscraper
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import BASE_URL, STORAGE_PATH, HEADERS, MAX_RETRIES, MAX_THREADS

class MangaCrawler:
    def __init__(self):
        self.session = self._create_session()
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )

    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        retry = Retry(total=MAX_RETRIES, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504, 429])
        session.mount("http://", HTTPAdapter(max_retries=retry))
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session

    def _make_request(self, url: str, headers: dict = None) -> requests.Response:
        """发送HTTP请求"""
        headers = headers or HEADERS
        for _ in range(MAX_RETRIES):
            try:
                response = self.session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if _ == MAX_RETRIES - 1:
                    raise Exception(f"请求失败 {url}: {str(e)}")
                time.sleep(random.uniform(2, 5))

    def _get_file_extension(self, url: str) -> str:
        """获取文件扩展名"""
        ext = os.path.splitext(url)[1]
        if ext:
            return ext
        mime_type, _ = mimetypes.guess_type(url)
        return mimetypes.guess_extension(mime_type) if mime_type else ".jpg"

    def _download_image(self, img_title: str, img_url: str, referer: str, chapter_path: str) -> None:
        """下载单张图片"""
        img_path = os.path.join(chapter_path, f"{img_title}{self._get_file_extension(img_url)}")
        if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
            return

        for _ in range(MAX_RETRIES):
            try:
                response = self.scraper.get(
                    img_url,
                    headers={**HEADERS, "referer": referer},
                    stream=True,
                    timeout=30
                )
                response.raise_for_status()

                temp_path = f"{img_path}.tmp"
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                if os.path.getsize(temp_path) > 0:
                    os.replace(temp_path, img_path)
                    return
                os.remove(temp_path)
                raise Exception("下载的文件大小为0")
            except Exception as e:
                if _ == MAX_RETRIES - 1:
                    raise Exception(f"图片下载失败 {img_title}: {str(e)}")
                time.sleep(random.uniform(2, 5))

    def search_manga(self, name: str) -> Dict[str, str]:
        """搜索漫画"""
        response = self._make_request(f"{BASE_URL}/?q={urllib.parse.quote(name)}")
        soup = BeautifulSoup(response.text, "html.parser")
        return {
            a.find("img").get("alt"): a.get("href")
            for a in soup.find_all("a", class_="site-card__link")
            if a.find("img") and a.get("href")
        }

    def get_chapters(self, manga_url: str) -> Dict[str, str]:
        """获取章节列表"""
        response = self._make_request(manga_url)
        soup = BeautifulSoup(response.text, "html.parser")
        return {
            a.find("img").get("alt"): a.get("href")
            for a in soup.find_all("a", class_="vstack gap-1 site-manga-thumbnail__link")
            if a.find("img") and a.get("href")
        }

    def download_chapter(self, chapter_title: str, chapter_url: str, manga_path: str) -> None:
        """下载单个章节"""
        chapter_path = os.path.join(manga_path, chapter_title)
        os.makedirs(chapter_path, exist_ok=True)

        for _ in range(3):
            try:
                response = self._make_request(chapter_url)
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
                        executor.submit(self._download_image, title, url, chapter_url, chapter_path)
                        for title, url in chapter_imgs.items()
                    ]
                    for future in as_completed(futures):
                        future.result()
                return
            except Exception as e:
                if _ == 2:
                    raise Exception(f"章节下载失败 {chapter_title}: {str(e)}")
                time.sleep(random.uniform(5, 10))

    def download_manga(self, manga_title: str, manga_url: str) -> None:
        """下载整部漫画"""
        manga_path = os.path.join(STORAGE_PATH, manga_title)
        os.makedirs(manga_path, exist_ok=True)

        chapters = self.get_chapters(manga_url)
        if not chapters:
            raise Exception("未找到任何章节")

        sorted_chapters = dict(sorted(chapters.items()))
        total_chapters = len(sorted_chapters)
        
        print(f"\n开始下载漫画: {manga_title}，共 {total_chapters} 章")
        with tqdm(total=total_chapters, desc="下载进度", unit="章", ncols=80) as pbar:
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                future_to_chapter = {
                    executor.submit(self.download_chapter, title, url, manga_path): title
                    for title, url in sorted_chapters.items()
                }
                
                for future in as_completed(future_to_chapter):
                    chapter_title = future_to_chapter[future]
                    try:
                        future.result()
                        pbar.update(1)
                        pbar.set_description(f"已完成: {chapter_title}")
                    except Exception as e:
                        print(f"\n章节 {chapter_title} 下载失败: {e}")

    def __del__(self):
        """确保资源被释放"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
            if hasattr(self, 'scraper'):
                self.scraper.close()
        except Exception:
            pass

def get_mangas(manga_name: str) -> Dict[str, str]:
    """获取漫画列表"""
    crawler = MangaCrawler()
    return crawler.search_manga(manga_name)

def download_manga(manga_title: str, manga_url: str) -> None:
    """下载漫画"""
    crawler = MangaCrawler()
    crawler.download_manga(manga_title, manga_url)
