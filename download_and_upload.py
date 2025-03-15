import os
import subprocess
import time
import threading
from huggingface_hub import HfApi, login

# 配置
HUGGINGFACE_TOKEN = os.environ["HUGGINGFACE_TOKEN"]
USERNAME = "servejjjhjj"  # 替换为你的 Hugging Face 用户名
REPO_NAME = "mp4-dataset"
REPO_TYPE = "dataset"
OUTPUT_FOLDER = "video_output"
VIDEO_URL = "http://0.0.0.0:16384/ysptp/cctv2.m3u8"

# 初始化 Hugging Face API
login(token=HUGGINGFACE_TOKEN)
api = HfApi()

def upload_video(file_path):
    """
    上传视频到 Hugging Face Hub
    """
    try:
        api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo=os.path.basename(file_path),
            repo_id=f"{USERNAME}/{REPO_NAME}",
            repo_type=REPO_TYPE,
            token=HUGGINGFACE_TOKEN
        )
        print(f"Uploaded {file_path} to Hugging Face Hub")
        os.remove(file_path)  # 上传完成后删除文件
        print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Failed to upload {file_path}: {e}")

def download_video():
    """
    使用 yt-dlp 下载视频，每 10 分钟分段一次
    """
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 使用 yt-dlp 下载视频
    command = [
        "yt-dlp",
        VIDEO_URL,
        "-o", f"{OUTPUT_FOLDER}/video_%(epoch)s.mp4",
        "--force-keyframes-at-cuts",  # 确保分段时关键帧对齐
        "--split-interval", "10",   # 每 10 分钟分段一次300
        "--no-continue",  # 不继续未完成的下载
        "--no-playlist",  # 仅下载单个视频
        "--retries", "10",  # 重试次数
        "--fragment-retries", "10",  # 分段重试次数
        "--concurrent-fragments", "5"  # 并发下载分段
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            print(output.strip().decode())

def monitor_and_upload():
    """
    监控视频文件夹并上传新文件
    """
    while True:
        files = os.listdir(OUTPUT_FOLDER)
        for file in files:
            if file.endswith(".mp4"):  # 只处理完整的 .mp4 文件
                file_path = os.path.join(OUTPUT_FOLDER, file)

                # 检查文件是否正在被写入
                if is_file_locked(file_path):
                    print(f"File {file_path} is still being written, skipping...")
                    continue

                # 上传文件
                upload_video(file_path)
        time.sleep(5)  # 每 10 秒检查一次

def is_file_locked(file_path):
    """
    检查文件是否被锁定（是否正在被写入）
    """
    try:
        with open(file_path, "a") as f:
            pass
        return False
    except IOError:
        return True

if __name__ == "__main__":
    # 启动下载线程
    download_thread = threading.Thread(target=download_video)
    download_thread.start()

    # 启动上传线程
    upload_thread = threading.Thread(target=monitor_and_upload)
    upload_thread.start()

    # 等待 3 小时后结束
    time.sleep(40)  # 3 小时 = 10800 秒
    print("Process completed after 3 hours.")
