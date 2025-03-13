import os
import os.path as osp
import re
import sys
import warnings
from typing import List, Union
import collections
import bs4
import requests
import itertools
import json
import argparse
#2025-02-05 02:06:29
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

    # finds the script tag with window['_DRIVE_ivd']
    encoded_data = None
    for script in folder_soup.select("script"):
        inner_html = script.decode_contents()

        if "_DRIVE_ivd" in inner_html:
            # first js string is _DRIVE_ivd, the second one is the encoded arr
            regex_iter = re.compile(r"'((?:[^'\\]|\\.)*)'").finditer(inner_html)
            # get the second elem in the iter
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

    # decodes the array and evaluates it as a python array
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
       # raise FolderContentsMaximumLimitError(message)
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


GoogleDriveFileToDownload = collections.namedtuple(
    "GoogleDriveFileToDownload", ("id", "path", "local_path")
)


def download_folder(proxy_, url=None, id=None, output=None, quiet=False, proxy=None, speed=None, use_cookies=True, remaining_ok=False, verify=True, user_agent=None, skip_download=False, resume=False) -> Union[List[str], List[GoogleDriveFileToDownload], None]:
    if not (id is None) ^ (url is None):
        raise ValueError("Either url or id has to be specified")
    if id is not None:
        url = "https://drive.google.com/drive/folders/{id}".format(id=id)
    if user_agent is None:
        # We need to use different user agent for folder download c.f., file
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"  # NOQA: E501

    sess = requests.session()
    sess.headers.update({'User-Agent': user_agent})

    if not quiet:
        print("Retrieving folder contents", file=sys.stderr)
    is_success, gdrive_file = _download_and_parse_google_drive_link(
        sess,
        url,
        quiet=quiet,
        remaining_ok=remaining_ok,
        verify=verify,
        proxy_=proxy_,
    )
    if not is_success:
        print("Failed to retrieve folder contents", file=sys.stderr)
        return None

    if not quiet:
        print("Retrieving folder contents completed", file=sys.stderr)
        print("Building directory structure", file=sys.stderr)
    directory_structure = _get_directory_structure(gdrive_file, previous_path="")
    if not quiet:
        print("Building directory structure completed", file=sys.stderr)



    print("——————————————————————————————————\n", directory_structure, "\n———————————文件列表完成———————————")
    sub_main(directory_structure)
    
     #directory_structure是一个文件夹一个文件夹逐个打印
"""
    if output is None:
        output = os.getcwd() + osp.sep
    if output.endswith(osp.sep):
        root_dir = osp.join(output, gdrive_file.name)
    else:
        root_dir = output
    if not skip_download and not osp.exists(root_dir):
        os.makedirs(root_dir)

    files = []
    for id, path in directory_structure:
        #root_dir绝对路径

        print(id, path, "测试点")
        local_path = osp.join(root_dir, path)

        if id is None:  # folder
            if not skip_download and not osp.exists(local_path):
                os.makedirs(local_path)
            continue

        if skip_download:
            files.append(
                GoogleDriveFileToDownload(id=id, path=path, local_path=local_path)
            )
        else:
            if resume and os.path.isfile(local_path):
                if not quiet:
                    print(
                        f"Skipping already downloaded file {local_path}",
                        file=sys.stderr,
                    )
                files.append(local_path)
                continue

            local_path = download(
                url=proxy_ + "https://drive.google.com/uc?id=" + id,
                output=local_path,
                quiet=quiet,
                proxy=proxy,
                speed=speed,
                use_cookies=use_cookies,
                verify=verify,
                resume=resume,
            )
            if local_path is None:
                if not quiet:
                    print("Download ended unsuccessfully", file=sys.stderr)
                return None
            files.append(local_path)
    if not quiet:
        print("Download completed", file=sys.stderr)
    return files
"""
#+++++++++++++

def clean_filename(filename): 
    try: 
        new_filename = filename.encode('utf-8', 'ignore').decode('utf-8') 
        
        return new_filename 
    except AttributeError: 
        # 如果filename不是字符串类型（例如None），则直接返回 
        return filename
        
def download_file(file_id, file_name, save_path): 
    url = f"https://c.map987.us.kg/https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"  
    try: 
        response = requests.get(url)  
        if response.status_code  == 200: 
            file_path = os.path.join(save_path,  file_name) 
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

def sub_main(data, ):
    for item in data: 
        if item[0] is not None: 
            file_id = item[0]
            file_name = item[1]
            file_name = clean_filename(file_name)
            save_path = os.getcwd()
            print(os.path.join(save_path,  file_name))
            print("↑保存路径")
            download_file(file_id, file_name, save_path) 
            
            
            
            
#++++++++++
def main():
    parser = argparse.ArgumentParser(description='Download Google Drive folder using proxy')
    parser.add_argument('--url', type=str, required=True, help='谷歌文件夹链接')
    parser.add_argument('--proxy', type=str, required=False, help='反代理链接，填写page.dev/，需实现page.dev/https://google.com能访问后面跟着的链接，注意要加/')
    parser.add_argument('--output', type=str, default=None, help='输出文件夹')
    args = parser.parse_args()


    
    #cloudflare workers代理绑定的域名，实现 https://aaa.workers.dev/https://google.com实际上访问https://google.com，注意末尾带/斜杠
    if args.proxy is None:
        args.proxy = ""
   # args.proxy = "https://c.map987.us.kg/"

    download_folder(url=args.url, proxy_=args.proxy, output=args.output)


if __name__ == "__main__":
    main()



"""
    
import os 
 
import re 
def read_file(file_path): 
    data = [] 
    with open(file_path, 'r', encoding="UTF-8-sig") as f: 
        lines = f.readlines()  
        for line in lines: 
            parts = eval(line.strip())  
            data.extend(parts)  
    return data 
 
 
import requests 
 
 

        
def main(): 
    file_path = "/storage/emulated/0/kkk.txt"  
    data = read_file(file_path) 
    save_path = "/storage/emulated/0/Download" 
    for item in data: 
        if item[0] is not None: 
            file_id = item[0] 
            print(file_id)
            file_name = item[1]
            file_name = clean_filename(file_name)
            download_file(file_id, file_name, save_path) 
 
 
if __name__ == "__main__": 
    main() 
 
"""     
