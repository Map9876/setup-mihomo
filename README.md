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
        uses: Map9876/setup-v2ray@vv #这里的@vv其实是GitHub action这些库的release的发布版本tags

        with:
         # config-base64: ${{ secrets.CONFIG_BASE64 }} # 你的 Base64 编码的 YAML 配置文件
          config-url: ${ secrets.CONFIG_URL } #yaml订阅链接，上面这个yaml，base64太长了问题是。二选一最好用这个
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


```yaml
#2025031209005
name: Debug Machine

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # 1. 检出代码
      - name: Checkout repository
        uses: actions/checkout@v3

      # 2. 设置 Mihomo（Clash）
      - name: Setup mihomo
        uses: ./ # 使用当前仓库中的 action
        with:
          config-url: ${{ secrets.CONFIG_URL }} # Clash YAML 订阅链接
          mihomo-version: "1.18.0" # 可选，默认是 1.18.0

      # 3. 配置代理环境变量
      - name: Create and configure ~/.bash_profile
        run: |
          echo 'function proxy_on() {
            export http_proxy=http://127.0.0.1:7890
            export https_proxy=http://127.0.0.1:7890
            export all_proxy=socks5://127.0.0.1:7890
            echo -e "终端代理已开启"
          }
          function proxy_off(){
            unset http_proxy https_proxy all_proxy
            echo -e "终端代理已关闭"
          }' > ~/.bash_profile
          source ~/.bash_profile
          proxy_on

      # 4. 安装 jq 和 bc（用于节点选择）
      - name: Install jq and bc
        run: |
          sudo apt-get update
          sudo apt-get install -y jq bc

      # 5. 选择最快的节点
      - name: Select fastest node
        run: |
          # 获取所有节点信息
          response=$(curl -s http://127.0.0.1:9090/proxies/🔰%20选择节点)
          echo "所有节点信息: $response"
          # 提取节点名称并进行 URL 编码
          nodes=$(echo "$response" | jq -r '.all[] | @uri')
          echo "可用节点: $nodes"
          # 测试每个节点的延迟
          fastest_node=""
          min_delay=999999
          for node in $nodes; do
            # 跳过 DIRECT 节点
            if [ "$node" == "DIRECT" ]; then
              echo "跳过 DIRECT 节点"
              continue
            fi
            echo "测试节点: $node"
            delay=$(curl -o /dev/null -s -w "%{time_total}\n" -x http://127.0.0.1:7890 http://1.1.1.1 --connect-timeout 10 --max-time 10)
            if [ $? -ne 0 ]; then
              echo "节点 $node 不可用，跳过"
              continue
            fi
            echo "节点 $node 的延迟: $delay 秒"
            # 比较延迟，选择最快的节点
            if (( $(echo "$delay < $min_delay" | bc -l) )); then
              min_delay=$delay
              fastest_node=$node
            fi
          done
          echo "最快节点: $fastest_node, 延迟: $min_delay 秒"
          # 选择最快节点
          curl -X PUT http://127.0.0.1:9090/proxies/🔰%20选择节点 -d "{\"name\":\"$(echo -n $fastest_node | jq -sRr @uri)\"}"
          echo "已选择最快节点: $fastest_node"

      # 6. 测试代理
      - name: Test proxy
        run: |
          curl -x http://127.0.0.1:7890 https://api.ip.sb/geoip

      # 7. 安装依赖
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release

      # 8. 启用额外仓库
      - name: Enable additional repositories
        run: |
          sudo apt-get update

      # 9. 安装 VNC 和桌面环境
      - name: Install VNC and Desktop Environment
        run: |
          sudo apt-get update
          sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
            xfce4 \
            xfce4-goodies \
            tightvncserver \
            novnc \
            python3 \
            python3-pip \
            git \
            firefox \
            xterm \
            xvfb

      # 10. 配置 VNC
      - name: Configure VNC
        run: |
          mkdir -p ~/.vnc
          echo "password" | vncpasswd -f > ~/.vnc/passwd
          chmod 600 ~/.vnc/passwd
          echo '#!/bin/bash
          # 加载代理环境变量
          source ~/.bash_profile
          export http_proxy=http://127.0.0.1:7890
          export https_proxy=http://127.0.0.1:7890
          export all_proxy=socks5://127.0.0.1:7890
          export DISPLAY=:1

          # 启动桌面环境
          startxfce4 &
          xhost +

          # 启动 Firefox
          export MOZ_USE_XINPUT2=1
          export MOZ_WEBRENDER=1
          firefox &' > ~/.vnc/xstartup
          chmod +x ~/.vnc/xstartup

      # 11. 启动 Xvfb（虚拟显示服务器）
      - name: Start Xvfb
        run: |
          Xvfb :99 -screen 0 1280x800x24 &
          export DISPLAY=:99

      # 12. 启动 VNC 服务器
      - name: Start VNC Server
        run: |
          vncserver :1 -geometry 1280x800 -depth 24
          sleep 5  # 等待 VNC 服务器启动

      # 13. 安装和配置 noVNC
      - name: Install and Setup noVNC
        run: |
          git clone https://github.com/novnc/noVNC.git
          cd noVNC
          ./utils/novnc_proxy --vnc localhost:5901 & # noVNC web 端口 6080

      # 14. 安装 Cloudflared
      - name: Install Cloudflared
        run: |
          wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
          sudo dpkg -i cloudflared-linux-amd64.deb

      # 15. 启动 Cloudflared 暴露 VNC 服务
      - name: Start Cloudflared for VNC
        run: |
          cloudflared tunnel --url tcp://localhost:5901 --protocol http2 &
          echo "等待 VNC 的 Cloudflared 隧道URL..."
          sleep 10
          ps aux | grep cloudflared

      # 16. 启动 Cloudflared 暴露 Mihomo Web UI
      - name: Start Cloudflared for Mihomo Web UI
        run: |
          cloudflared tunnel --url http://localhost:9090 &
          echo "等待 Mihomo Web UI 的 Cloudflared 隧道URL..."
          sleep 10
          ps aux | grep cloudflared

      # 17. 启动 Cloudflared 暴露 noVNC
      - name: Start Cloudflared for noVNC
        run: |
          cloudflared tunnel --url http://localhost:6080 --protocol http2 &
          echo "等待 noVNC 的 Cloudflared 隧道URL..."
          sleep 10
          ps aux | grep cloudflared

      # 18. 保持运行并监控
      - name: Keep Alive and Monitor
        run: |
          echo "=== Firefox VNC Server Information ==="
          echo "noVNC端口: 6080"
          echo "VNC端口: 5901"
          echo "VNC密码: password"
          echo "说明: 使用浏览器连接时，主机地址使用上面cloudflared生成的域名"
          echo "端口使用: 复制cloudflared URL后的端口号"
          echo "=== Mihomo Web UI Information ==="
          echo "Web UI端口: 9090"
          echo "说明: 使用浏览器连接时，主机地址使用上面cloudflared生成的域名"
          echo "端口使用: 复制cloudflared URL后的端口号"
          while true; do
            echo "=== Status Update $(date) ==="
            sleep 300
          done
```


远程：

```
echo "admin" | vncpasswd -f > ~/.vnc/passwd # 这里admin是密码

vncserver :1 -geometry 1280x1024 -depth 24

cloudflared tunnel --url tcp://localhost:5901 --protocol http2 &
#会打印出一个任意的链接，比如https://components-berkeley-recipient-chelsea.trycloudflare.com
```

本地：

```
apt install cloudflared

cloudflared access tcp --url localhost:5091 --hostname https://components-berkeley-recipient-chelsea.trycloudflare.com
#此处的链接是上方得到的链接

#然后在vnc查看器，比如vnc viewer，avnc等，输入localhost 5091分别作为ip和端口，admin为密码即可。5091随便修改
```
