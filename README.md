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



```
name: Debug Machine

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup mihomo
        uses: ./ # 使用当前仓库中的 action
        with:
          config-url: ${{ secrets.CONFIG_URL }} # Clash YAML 订阅链接
          mihomo-version: "1.18.0" # 可选，默认是 1.18.0

      - name: Start proxy
        run: |
          curl -X PUT http://127.0.0.1:9090/proxies/🔰%20选择节点 -d '{"name":"🇯🇵 免费-日本4-Ver.7"}'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y tigervnc-standalone-server firefox xterm novnc

      - name: Configure VNC
        run: |
          mkdir -p ~/.vnc
          echo "#!/bin/sh" > ~/.vnc/xstartup
          echo "tigervncserver -xstartup /usr/bin/xterm" >> ~/.vnc/xstartup  # 启动 xterm
          echo "firefox &" >> ~/.vnc/xstartup  # 启动 firefox
          chmod +x ~/.vnc/xstartup

      - name: Set VNC password
        run: |
          echo "password" | vncpasswd -f > ~/.vnc/passwd
          chmod 600 ~/.vnc/passwd

      - name: Start VNC server
        run: |
          vncserver :1 -geometry 1280x1024 -depth 24

      - name: Start noVNC
        run: |
          /usr/bin/websockify --web /usr/share/novnc 6080 localhost:5901 &
          echo "noVNC 已启动，端口为 6080"

      - name: Setup Cloudflared
        run: |
          sleep 5
          wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
          chmod +x cloudflared
          sudo mv cloudflared /usr/local/bin/
          export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
          cloudflared tunnel --url http://127.0.0.1:6080 2>&1 | tee cloudflared.log &
          sleep 10
          cat cloudflared.log | grep "trycloudflare"

      - name: Test proxy
        env:
          http_proxy: "http://127.0.0.1:7890"
          https_proxy: "http://127.0.0.1:7890"
        run: |
          curl -x http://127.0.0.1:7890 https://api.live.bilibili.com/ip_service/v1/ip_service/get_ip_addr
          sleep 3000
```          
          
          
          
```          
name: Debug Machine

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup mihomo
        uses: ./ # 使用当前仓库中的 action
        with:
          config-url: ${{ secrets.CONFIG_URL }} # Clash YAML 订阅链接
          mihomo-version: "1.18.0" # 可选，默认是 1.18.0

      - name: Start proxy
        run: |
          curl -X PUT http://127.0.0.1:9090/proxies/🔰%20选择节点 -d '{"name":"🇯🇵 免费-日本4-Ver.7"}'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y tigervnc-standalone-server firefox xterm

      - name: Configure VNC
        run: |
          mkdir -p ~/.vnc
          echo "#!/bin/sh" > ~/.vnc/xstartup
          echo "tigervncserver -xstartup /usr/bin/xterm" >> ~/.vnc/xstartup  # 启动 xterm
          echo "firefox &" >> ~/.vnc/xstartup  # 启动 firefox
          chmod +x ~/.vnc/xstartup

      - name: Set VNC password
        run: |
          echo "password" | vncpasswd -f > ~/.vnc/passwd
          chmod 600 ~/.vnc/passwd

      - name: Start VNC server
        run: |
          vncserver :1 -geometry 1280x1024 -depth 24

      - name: Setup Cloudflared
        run: |
          sleep 10
          export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
          wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
          chmod +x cloudflared
          sudo mv cloudflared /usr/local/bin/
          cloudflared tunnel --url http://127.0.0.1:6080 2>&1 | tee cloudflared.log &
          sleep 10
          cat cloudflared.log | grep "trycloudflare"

      - name: Test proxy
        env:
          http_proxy: "http://127.0.0.1:7890"
          https_proxy: "http://127.0.0.1:7890"
        run: |
          curl -x http://127.0.0.1:7890 https://api.live.bilibili.com/ip_service/v1/ip_service/get_ip_addr
          curl https://abema.com
          sleep 3000

      - name: Set up Python3
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Set up Chromedriver
        uses: nanasess/setup-chromedriver@v2

      - name: Start browser
        run: |
          export DISPLAY=:99
          chromedriver --url-base=/wd/hub &
          sudo Xvfb -ac :99 -screen 0 1280x1024x24 > /dev/null 2>&1 & # 可选

      - name: Install Chrome
        run: |
          sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
          sudo apt update
          sudo apt-get install -y google-chrome-stable

      - name: Install requirements
        run: |
          python3 -m pip install --upgrade pip
          pip3 install selenium

      - name: Take screenshot of abema.com
        run: |
          export DISPLAY=:99
          python3 - <<EOF
          from selenium import webdriver
          from selenium.webdriver.chrome.service import Service
          from selenium.webdriver.common.by import By
          import time

          # 设置 Chrome 选项
          options = webdriver.ChromeOptions()
          options.add_argument('--no-sandbox')
          options.add_argument('--disable-dev-shm-usage')
          options.add_argument('--headless')  # 无头模式
          options.add_argument('--disable-gpu')

          # 启动 ChromeDriver
          service = Service(executable_path='/usr/local/bin/chromedriver')
          driver = webdriver.Chrome(service=service, options=options)

          # 打开 abema.com
          driver.get("https://abema.com")
          time.sleep(5)  # 等待页面加载

          # 截图
          driver.save_screenshot('abema_screenshot.png')
          driver.quit()
          EOF

      - name: Upload screenshot
        uses: actions/upload-artifact@v3
        with:
          name: abema-screenshot
          path: abema_screenshot.png
```          
          
          
          

```
name: debug machine
on:
  workflow_dispatch:
jobs:

  setup-proxy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup mihomo
        uses: ./
        with:
          config-url: ${{ secrets.CONFIG_URL }} # clash yaml订阅链接
          mihomo-version: "1.18.0" # 可选，默认是 1.18.0
      - name: cloudflared 
        run: |
          sleep 5
          wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
          chmod +x cloudflared
          sudo mv cloudflared /usr/local/bin/
          cloudflared tunnel --url http://127.0.0.1:9090 2>&1 | tee cloudflared.log &
          sleep 10
          cat cloudflared.log | grep "trycloudflare"
    
      - name: Test proxy
        env:
          http_proxy: "http://127.0.0.1:7890"
          https_proxy: "http://127.0.0.1:7890"

        run: |
          
          #curl http://127.0.0.1:9090/ui/
          curl -X PUT http://127.0.0.1:9090/proxies/🔰%20选择节点 -d '{"name":"🇯🇵 免费-日本4-Ver.7"}'
          curl -x http://127.0.0.1:7890 https://api.live.bilibili.com/ip_service/v1/ip_service/get_ip_addr
          sleep 3000      
```   
