import os
import re
import pyfiglet
import img2pdf
from PIL import Image

output_dir = "manga_library"
os.makedirs(output_dir, exist_ok=True)


def natural_sort_key(text):
    """
    自然排序关键函数：按字符串中的数字和字符顺序排序。
    """
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', text)]


def is_image(file_path):
    """
    检查文件是否为有效图片。
    """
    try:
        with Image.open(file_path) as img:
            return True
    except:
        return False


def get_sorted_files(source_dir: str, extensions: list) -> list:
    """
    获取目录中的所有图片文件，按自然顺序排序。
    """
    return sorted(
        [
            os.path.join(source_dir, file)
            for file in os.listdir(source_dir)
            if os.path.isfile(os.path.join(source_dir, file)) and os.path.splitext(file)[1].lower() in extensions
        ],
        key=natural_sort_key  # 按自然排序
    )


def create_pdf(manga_name: str, storage_path: str = "storage") -> None:
    """
    遍历漫画目录，整合所有章节并生成一个 PDF。
    """
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    manga_path = os.path.join(storage_path, manga_name)

    if not os.path.isdir(manga_path):  # 如果漫画文件夹不存在
        print(f"漫画文件夹 '{manga_name}' 不存在于 '{storage_path}' 中。")
        return

    all_images = []

    # 遍历每个章节并按自然顺序处理
    for chapter_name in sorted(os.listdir(manga_path), key=natural_sort_key):
        chapter_path = os.path.join(manga_path, chapter_name)

        if os.path.isdir(chapter_path):  # 如果是章节文件夹
            chapter_images = get_sorted_files(chapter_path, image_extensions)
            all_images.extend([img for img in chapter_images if is_image(img)])

    # 如果有图片，生成 PDF
    if all_images:
        print(f"正在处理漫画：{manga_name}")

        output_pdf = os.path.join(output_dir, f"{manga_name}.pdf")
        try:
            with open(output_pdf, "wb") as f:
                f.write(img2pdf.convert(all_images))
            print(f"PDF 已生成：{output_pdf}")
        except Exception as e:
            print(f"生成 PDF 时出错：{e}")
    else:
        print(f"漫画 '{manga_name}' 没有找到任何有效图片文件。")


def create_ascii_art(text: str, font: str = "slant") -> str:
    """
    将文本转换为ASCII艺术字
    :param text: 文本
    :param font: 字体
    :return: ASCII艺术字
    """
    ascii_art = pyfiglet.figlet_format(text, font=font)
    return ascii_art


if __name__ == "__main__":
    print(create_ascii_art("Manga Library"))
    create_pdf("夏日重现2026 未发生的事故住宅")
