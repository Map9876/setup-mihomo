import requests
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)


@app.route("/proxy/<path:url>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(url):
    """通用的反向代理。"""
    try:
        # 构造目标 URL
        target_url = f"https://{url}"

        # 获取客户端请求的头部信息
        headers = {key: value for (key, value) in request.headers if key.lower() != "host"}

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
    app.run(host="0.0.0.0", port=3000)
