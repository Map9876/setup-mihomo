"""
import requests
import re
from urllib.parse import unquote

# 定义URL和请求头
url = 'https://c.map987.us.kg/https://app.box.com/index.php?folder_id=307393495021&q%5Bshared_item%5D%5Bshared_name%5D=9kyetxelu85r7o3ipyytadxbygm0r8x9&rm=box_v2_zip_shared_folder'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'X-Box-Client-Name': 'enduserapp',
    'X-Box-Client-Version': '23.54.1',
    'Alt-Used': 'app.box.com',
    'Connection': 'keep-alive',
    'Referer': 'https://app.box.com/s/9kyetxelu85r7o3ipyytadxbygm0r8x9',
    'Cookie': 'z=sjqt3qd249h16eul6l40a80sjm; box_visitor_id=67c859d47d52e2.25286109; bv=MONO-8203; cn=30; site_preference=desktop; anonymousbanner=seen',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'TE': 'trailers'
}

# 发送请求
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    # 解析 JSON 响应
    try:
        json_data = response.json()
        print("JSON 数据:")
        print(json_data)

        # 提取下载链接
        download_url = json_data.get("download_url")
        if download_url:
            # 修复下载链接中的反斜杠
            download_url = download_url.replace("\\/", "/")
            print("修复后的下载链接:", download_url)

            # 下载文件
            file_response = requests.get(download_url, headers=headers, stream=True)
            if file_response.status_code == 200:
                # 从 Content-Disposition 头中提取文件名
                content_disposition = file_response.headers.get("Content-Disposition")
                if content_disposition:
                    # 提取文件名，例如：attachment; filename="2025_Gameplay_Update.zip"
                    filename = re.findall('filename="?(.+)"?', content_disposition)[0]
                    filename = unquote(filename)  # 解码 URL 编码的文件名
                    print(filename)
                else:
                    # 如果 Content-Disposition 不存在，从 URL 中提取文件名
                    filename = re.findall('ZipFileName=([^&]+)', download_url)[0]
                    filename = unquote(filename)  # 解码 URL 编码的文件名

                print("保存文件名:", filename)

                # 保存文件
                with open(filename, "wb") as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("文件下载成功。")
            else:
                print(f"文件下载失败，状态码: {file_response.status_code}")
        else:
            print("JSON 数据中未找到 download_url。")
    except ValueError as e:
        print("响应内容不是有效的 JSON 格式:", e)
else:
    print(f"请求失败，状态码: {response.status_code}")
    
"""    
"""    


文件termuxAndroidHelpers/bin
/box.com-folder-download.sh 最终出点文件
#!/bin/bash

# https://app.box.com/s/q3w7cqks1ur1o2c21moiuf8nbahag7xq
url="$1"
target="$2"

share="${url##*/}"
wget "$url" -O "$share"
id=$(html_prettyprint.py "$share" | grep postStreamData | sed -e 's/.*,"folder":\({[^}]*}\).*/\1/' | sed -e 's/.*"id":\([^,]*\).*/\1/')

wget "https://app.box.com/index.php?folder_id=${id}&q%5Bshared_item%5D%5Bshared_name%5D=${share}&rm=box_v2_zip_shared_folder" -O $id

get=$(cat "$id" |json_prettyprint|grep download_url |cut -d '"' -f 4)
name="${get##*ZipFileName=}"
name=$(echo ${name%%\&*} | python3 -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));")

wget "$get" -O "$name" && rm "$share" "$id"    

文件termuxAndroidHelpers/bin
/html_prettyprint.py：
format_html.py

文件termuxAndroidHelpers/bin
/format_html.py：
../external/format_html.py

文件termuxAndroidHelpers/external
/format_html.py：
#!/bin/python3
##
# This is a quick script that will format/indent HTML
# HTML Tidy is often too destructive, especially with bad HTML, so we're using Beautiful Soup
##
# USAGE: Designed to be used on the command line, just pipe HTML to it, and it will output
#         cat file.html | python format_html.py
### 
# Download & Install Beautiful Soup, if you don't have it already:
# Go to the Beautiful Soup web site, http://www.crummy.com/software/BeautifulSoup/
# Download the package
# Unpack it
# In a Terminal window, cd to the resulting directory
# Type python setup.py install

#
# http://stackoverflow.com/questions/6150108/python-how-to-pretty-print-html-into-a-file
from bs4 import BeautifulSoup as bs
import sys

# This is one way to load a file into a variable:
# lh = open("/Users/mruten/Projects/jacksontriggs/app/assets/javascripts/jt/contactUsComments.html").read()

# But, we'll read from standard input, so we can pipe output to it
# i.e. run with cat filename.html | this_file.py
raw = sys.stdin
out = sys.stdout
if len(sys.argv) == 3:
    raw = open(sys.argv[1], 'r')
    out = open(sys.argv[2], 'w+')
elif len(sys.argv) == 2 and sys.argv[1] == "-h":
    print("usage: cat html | " + sys.argv[0] + " > out")
    print("\t" + sys.argv[0] + " infile outfile")
    sys.exit(0)
elif len(sys.argv) == 2:
    raw = open(sys.argv[1], 'r')


data = raw.readlines()
raw.close()
# print "Counted", len(data), "lines."
data = "".join(data)
# die
#sys.exit()

#root = data.tostring(sliderRoot) #convert the generated HTML to a string
soup = bs(data, features="html.parser")                #make BeautifulSoup
prettyHTML=soup.prettify()   #prettify the html

out.write(prettyHTML)
out.close()
# print (prettyHTML)

"""


import requests
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
import json

def download_file(url, target=None, use_proxy=False):
    """
    从 Box.com 共享链接下载文件
    :param url: Box.com 共享链接
    :param target: 目标文件名（可选）
    :param use_proxy: 是否使用代理前置（可选）
    """
    # 如果启用代理前置，则在 URL 前添加代理前缀
    if use_proxy:
        proxy_prefix = "https://c.map987.us.kg/"
        url = proxy_prefix + url  # 直接拼接代理前缀和原始 URL
        print(f"使用代理前置后的 URL: {url}")

    # 提取共享链接的文件名部分
    share = url.split("/")[-1]
    print(f"共享链接的文件名部分: {share}")

    # 下载共享链接的页面内容
    print(f"正在下载共享链接页面: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"下载共享链接页面失败，状态码: {response.status_code}")
        return

    # 使用 BeautifulSoup 解析 HTML 并提取 folder_id
    print("正在提取 folder_id...")
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", string=re.compile(r'Box\.postStreamData'))
    if not script_tag:
        print("无法从页面中提取 Box.postStreamData。")
        return

    # 提取 Box.postStreamData 中的 folder_id
    match = re.search(r'"currentFolderID":(\d+)', script_tag.string)
    if not match:
        print("无法从 Box.postStreamData 中提取 folder_id。")
        return

    folder_id = match.group(1)
    print(f"提取的 folder_id: {folder_id}")

    # 构建下载链接
    download_url = f"https://app.box.com/index.php?folder_id={folder_id}&q%5Bshared_item%5D%5Bshared_name%5D={share}&rm=box_v2_zip_shared_folder"
    if use_proxy:
        download_url = proxy_prefix + download_url  # 直接拼接代理前缀和下载链接
    print(f"构建的下载链接: {download_url}")

    # 下载 JSON 数据
    print("正在下载 JSON 数据...")
    response = requests.get(download_url)
    if response.status_code != 200:
        print(f"下载 JSON 数据失败，状态码: {response.status_code}")
        return

    # 解析 JSON 数据
    try:
        json_data = response.json()
    except json.JSONDecodeError:
        print("下载的 JSON 数据格式无效。")
        return

    # 提取文件下载链接
    print("正在提取文件下载链接...")
    file_download_url = json_data.get("download_url")
    if not file_download_url:
        print("无法从 JSON 中提取下载链接。")
        return
    print(f"提取的文件下载链接: {file_download_url}")

    # 提取文件名
    file_name = re.search(r"ZipFileName=([^&]+)", file_download_url)
    if file_name:
        file_name = unquote(file_name.group(1))
    else:
        file_name = "downloaded_file.zip"  # 默认文件名
    print(f"提取的文件名: {file_name}")

    # 如果未指定目标文件名，则使用服务器提供的文件名
    if not target:
        target = file_name

    # 下载文件并保存
    print(f"正在下载文件: {target}")
    response = requests.get(file_download_url, stream=True)
    if response.status_code != 200:
        print(f"文件下载失败，状态码: {response.status_code}")
        return

    with open(target, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"文件下载成功: {target}")
"""
if __name__ == "__main__":
    # Box.com 共享链接
    url = "https://app.box.com/s/9kyetxelu85r7o3ipyytadxbygm0r8x9"

    # 目标文件名（可选）
    target = None  # 如果不指定，则使用服务器提供的文件名

    # 是否使用代理前置（可选）
    use_proxy = True  # 设置为 True 启用代理前置

    # 调用下载函数
    download_file(url, target, use_proxy)

"""

    

if __name__ == "__main__":
    import sys

    # 检查参数
    if len(sys.argv) < 2:
        print("Usage: python box_downloader.py <box.com共享链接> [目标文件名。如果不指定，则使用服务器提供的文件名]")
        exit()
        url = "https://app.box.com/s/9kyetxelu85r7o3ipyytadxbygm0r8x9"
        print(f"下载 {url} 中")

    # 获取共享链接和目标文件名
    url = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None
    use_proxy = True  # 设置为 True 启用代理前置

    # 调用下载函数
    download_file(url, target, use_proxy)
    
    
    
