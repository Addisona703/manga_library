import os
import re
from typing import List
import pyfiglet
import img2pdf
from PIL import Image
from rich import print
from rich.text import Text
from rich.console import Console
from config import OUTPUT_DIR, STORAGE_PATH

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

def natural_sort_key(text: str) -> List:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', text)]

def is_image(file_path: str) -> bool:
    try:
        with Image.open(file_path) as _: return True
    except: return False

def get_sorted_files(source_dir: str) -> List[str]:
    source_dir = os.path.normpath(source_dir)
    return sorted(
        [
            os.path.normpath(os.path.join(source_dir, file))
            for file in os.listdir(source_dir)
            if os.path.isfile(os.path.join(source_dir, file)) 
            and os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS
        ],
        key=natural_sort_key
    )

def create_pdf(manga_name: str, storage_path: str = STORAGE_PATH) -> None:
    manga_path = os.path.normpath(os.path.join(storage_path, manga_name))
    if not os.path.isdir(manga_path):
        print(f"漫画文件夹 '{manga_name}' 不存在于 '{storage_path}' 中。")
        return

    all_images = []
    for chapter_name in sorted(os.listdir(manga_path), key=natural_sort_key):
        chapter_path = os.path.normpath(os.path.join(manga_path, chapter_name))
        if os.path.isdir(chapter_path):
            chapter_images = get_sorted_files(chapter_path)
            all_images.extend([os.path.normpath(img) for img in chapter_images if is_image(img)])

    if not all_images:
        print(f"漫画 '{manga_name}' 没有找到任何有效图片文件。")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_pdf = os.path.normpath(os.path.join(OUTPUT_DIR, f"{manga_name}.pdf"))
    try:
        print(f"正在处理漫画：{manga_name}")
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(all_images))
        print(f"PDF 已生成：{output_pdf}")
    except Exception as e:
        print(f"生成 PDF 时出错：{e}")

def create_ascii_art(text: str, font: str = "slant") -> Text:
    ascii_art = pyfiglet.figlet_format(text, font=font)
    gradient_text = Text()
    colors = [
        "#FF0000", "#FF4000", "#FF8000", "#FFBF00", 
        "#FFFF00", "#80FF00", "#00FF00", "#00FF80", 
        "#00FFFF", "#0080FF", "#0000FF", "#4B0082"
    ]
    
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        try:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
    non_empty_lines = [line for line in ascii_art.split('\n') if line.strip()]
    total_lines = len(non_empty_lines)
    
    lines = ascii_art.split('\n')
    color_index = 0
    for line in lines:
        if line.strip():
            color = colors[int((color_index * (len(colors) - 1)) / (total_lines - 1 or 1)) % len(colors)]
            gradient_text.append(line + '\n', style=f"bold {color}")
            color_index += 1
        else:
            gradient_text.append('\n')
    
    return gradient_text

if __name__ == "__main__":
    console = Console()
    console.print(create_ascii_art("Manga Library"))
    create_pdf("路人超能100 官方设定集")
