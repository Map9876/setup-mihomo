import os
import os.path as osp
import re
import sys
import warnings
import shutil
import zipfile
from typing import List, Union
import collections
import bs4
import requests
import itertools
import json
import argparse
from datetime import datetime  # 新增：用于生成时间戳

# 常量
MAX_NUMBER_FILES = 50


class _GoogleDriveFile(object):
    TYPE_FOLDER = "application/vnd.google-apps.folder"

    def __init__(self, id, name, type, children=None):
        self.id = id
        self.name = name
        self.type = type
        self.children = children if children is not None else []

    def is_folder(self):
        return self.type == self.TYPE_FOLDER


def _parse_google_drive_file(url, content):
    """Extracts information about the current page file and its children."""
    folder_soup = bs4.BeautifulSoup(content, features="html.parser")

    # 查找包含 _DRIVE_ivd 的 script 标签
    encoded_data = None
    for script in folder_soup.select("script"):
        inner_html = script.decode_contents()

        if "_DRIVE_ivd" in inner_html:
            # 第一个 js 字符串是 _DRIVE_ivd，第二个是编码的数组
            regex_iter = re.compile(r"'((?:[^'\\]|\\.)*)'").finditer(inner_html)
            try:
                encoded_data = next(itertools.islice(regex_iter, 1, None)).group(1)
            except StopIteration:
                raise RuntimeError("Couldn't find the folder encoded JS string")
            break

    if encoded_data is None:
        raise RuntimeError(
            "Cannot retrieve the folder information from the link. "
            "You may need to change the permission to "
            "'Anyone with the link', or have had many accesses. "
            "Check FAQ in https://github.com/wkentaro/gdown?tab=readme-ov-file#faq.",
        )

    # 解码数组并解析为 Python 数组
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        decoded = encoded_data.encode("utf-8").decode("unicode_escape")
    folder_arr = json.loads(decoded)

    folder_contents = [] if folder_arr[0] is None else folder_arr[0]

    sep = " - "  # unicode dash
    splitted = folder_soup.title.contents[0].split(sep)
    if len(splitted) >= 2:
        name = sep.join(splitted[:-1])
    else:
        raise RuntimeError(
            "file/folder name cannot be extracted from: {}".format(
                folder_soup.title.contents[0]
            )
        )

    gdrive_file = _GoogleDriveFile(
        id=url.split("/")[-1],
        name=name,
        type=_GoogleDriveFile.TYPE_FOLDER,
    )

    id_name_type_iter = [
        (e[0], e[2].encode("raw_unicode_escape").decode("utf-8"), e[3])
        for e in folder_contents
    ]

    return gdrive_file, id_name_type_iter


def _download_and_parse_google_drive_link(sess, url, proxy_, quiet=False, remaining_ok=False, verify=True):
    """Get folder structure of Google Drive folder URL."""
    return_code = True
    url_ = proxy_ + url
    for _ in range(2):
        res = sess.get(url_, verify=verify)
        url = res.url

    gdrive_file, id_name_type_iter = _parse_google_drive_file(
        url=url,
        content=res.text,
    )

    for child_id, child_name, child_type in id_name_type_iter:
        if child_type != _GoogleDriveFile.TYPE_FOLDER:
            if not quiet:
                print(
                    "Processing file",
                    child_id,
                    child_name,
                )
            gdrive_file.children.append(
                _GoogleDriveFile(
                    id=child_id,
                    name=child_name,
                    type=child_type,
                )
            )
            if not return_code:
                return return_code, None
            continue

        if not quiet:
            print(
                "Retrieving folder",
                child_id,
                child_name,
            )
        return_code, child = _download_and_parse_google_drive_link(
            sess=sess,
            url="https://drive.google.com/drive/folders/" + child_id,
            proxy_=proxy_,
            quiet=quiet,
            remaining_ok=remaining_ok,
        )
        if not return_code:
            return return_code, None
        gdrive_file.children.append(child)
    has_at_least_max_files = len(gdrive_file.children) == MAX_NUMBER_FILES
    if not remaining_ok and has_at_least_max_files:
        message = " ".join(
            [
                "The gdrive folder with url: {url}".format(url=url),
                "has more than {max} files,".format(max=MAX_NUMBER_FILES),
                "gdrive can't download more than this limit.",
            ]
        )
        raise RuntimeError(message)
    return return_code, gdrive_file


def _get_directory_structure(gdrive_file, previous_path):
    """Converts a Google Drive folder structure into a local directory list."""
    directory_structure = []
    for file in gdrive_file.children:
        file.name = file.name.replace(osp.sep, "_")
        if file.is_folder():
            directory_structure.append((None, osp.join(previous_path, file.name)))
            for i in _get_directory_structure(file, osp.join(previous_path, file.name)):
                directory_structure.append(i)
        elif not file.children:
            directory_structure.append((file.id, osp.join(previous_path, file.name)))
    return directory_structure


def clean_filename(filename):
    """清理文件名中的非法字符。"""
    try:
        new_filename = filename.encode('utf-8', 'ignore').decode('utf-8')
        return new_filename
    except AttributeError:
        return filename


def download_file(file_id, file_name, save_path):
    """下载单个文件。"""
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_path = os.path.join(save_path, file_name)
            dir_name = os.path.dirname(file_path)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Successfully downloaded {file_name} to {file_path}")
        else:
            print(f"Failed to download {file_name}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")


def zip_directory(directory_path, output_zip_path):
    """将目录打包为 ZIP 文件。"""
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)
    print(f"Successfully zipped {directory_path} to {output_zip_path}")


def sub_main(data, output_dir):
    """下载文件并打包为 ZIP 文件。"""
    for item in data:
        if item[0] is not None:
            file_id = item[0]
            file_name = item[1]
            file_name = clean_filename(file_name)
            download_file(file_id, file_name, output_dir)

    # 打包下载的文件，以时间命名压缩包
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 生成时间戳
    zip_file_name = f"downloaded_files_{timestamp}.zip"  # 以时间命名压缩包
    zip_file_path = os.path.join(output_dir, zip_file_name)
    zip_directory(output_dir, zip_file_path)
    print(f"All files have been zipped to {zip_file_path}")


def main():
    parser = argparse.ArgumentParser(description='Download Google Drive folder using proxy')
    parser.add_argument('--url', type=str, required=True, help='谷歌文件夹链接')
    parser.add_argument('--proxy', type=str, required=False, help='反代理链接，填写page.dev/，需实现page.dev/https://google.com能访问后面跟着的链接，注意要加/')
    parser.add_argument('--output', type=str, default=None, help='输出文件夹')
    args = parser.parse_args()

    # 设置代理
    if args.proxy is None:
        args.proxy = ""
    args.proxy = ""

    # 下载文件夹
    is_success, gdrive_file = _download_and_parse_google_drive_link(
        requests.session(),
        args.url,
        proxy_=args.proxy,
    )
    if not is_success:
        print("Failed to retrieve folder contents", file=sys.stderr)
        return

    # 获取目录结构
    directory_structure = _get_directory_structure(gdrive_file, previous_path="")

    # 设置输出目录
    if args.output is None:
        args.output = os.getcwd()
    
    # 创建以时间命名的文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output, f"download_{timestamp}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 下载文件并打包
    sub_main(directory_structure, output_dir)


if __name__ == "__main__":
    main()
