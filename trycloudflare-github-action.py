import requests
from flask import Flask, request, Response, stream_with_context
from urllib.parse import urlparse, unquote

app = Flask(__name__)


@app.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy():
    """通用的反向代理。"""
    try:
        # 获取目标 URL
        target_url = request.args.get("url")
        if not target_url:
            return "请提供目标 URL（例如：/?url=https://example.com）", 400

        # 解码 URL
        target_url = unquote(target_url)

        # 解析传入的 URL
        parsed_url = urlparse(target_url)

        # 如果 URL 没有协议头，默认使用 HTTPS
        if not parsed_url.scheme:
            target_url = f"https://{target_url}"
            parsed_url = urlparse(target_url)

        # 构造目标 URL
        target_url = parsed_url.geturl()

        # 获取客户端请求的头部信息
        headers = {key: value for (key, value) in request.headers if key.lower() != "host"}

        # 删除 Origin 和 Referer 请求头
        headers.pop("Origin", None)
        headers.pop("Referer", None)

        # 转发请求到目标 URL
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            stream=True,  # 启用流式传输
        )

        # 将目标网站的响应返回给客户端
        return Response(
            stream_with_context(response.iter_content(chunk_size=8192)),
            status=response.status_code,
            headers=dict(response.headers),
        )
    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    # 启动 Flask 服务器
    app.run(host="0.0.0.0", port=3000)
