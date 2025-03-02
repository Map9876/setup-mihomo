https://chat.deepseek.com/a/chat/s/8f675fff-f8fa-4d70-9692-e8cdbff6483d

```
jobs:
  setup-proxy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup mihomo
       # uses: ./.github/actions/setup-mihomo yaml在自己储存库可以这样写
        uses: Map9876/setup-v2ray@mm #这里的mm其实是GitHub action这些库的release的发布版本tags

        with:
          config-base64: ${{ secrets.CONFIG_BASE64 }} # 你的 Base64 编码的 YAML 配置文件
          mihomo-version: "1.18.0" # 可选，默认是 1.18.0

      - name: Test proxy
        run: |
          curl -x http://127.0.0.1:7890 https://api.live.bilibili.com/ip_service/v1/ip_service/get_ip_addr
        env:
          http_proxy: "http://127.0.0.1:7890"
          https_proxy: "http://127.0.0.1:7890"
```
### 配置说明

1. **`config-base64`**:
   - 这是一个 Base64 编码的 YAML 配置文件。你可以使用以下命令将你的clash YAML 文件转换为 Base64：
     ```bash
     base64 -w 0 config.yaml
     ```
   - 将生成的 Base64 字符串保存到 GitHub Secrets 中（例如 `CONFIG_BASE64`）。
  
### 测试代理

在工作流中，你可以使用 `curl` 命令测试代理是否正常工作。例如：

```yaml
- name: Test proxy
  run: |
    curl -x http://127.0.0.1:7890 https://api.live.bilibili.com/ip_service/v1/ip_service/get_ip_addr
  env:
    http_proxy: "http://127.0.0.1:7890"
    https_proxy: "http://127.0.0.1:7890"
```
