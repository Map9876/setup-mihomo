
import os
import subprocess
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
DOWNLOAD_DIR = os.path.expanduser("~/files")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        filename = request.form.get("filename")
        content = request.form.get("content")
        if filename and content:
  with open(os.path.join(DOWNLOAD_DIR, filename), "w") as f:
      f.write(content)
  return f"文件 {filename} 已创建！"

    files = os.listdir(DOWNLOAD_DIR)
    file_links = "\n".join(
        f"<li><a href='http://localhost:8080/{file}' target='_blank'>{file}</a></li>"
        for file in files
    )
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>命令执行器和文件下载</title>
  <style>
      body, html {
margin: 0;
padding: 0;
height: 100%;
font-family: Arial, sans-serif;
      }
      .input-container {
width: 100%;
height: 10%;
display: flex;
align-items: center;
justify-content: center;
background-color: #f0f0f0;
      }
      .input-container input {
width: 80%;
height: 50%;
font-size: 16px;
padding: 10px;
border: 1px solid #ccc;
border-radius: 5px;
      }
      pre {
background-color: #f8f8f8;
padding: 10px;
border: 1px solid #ddd;
border-radius: 5px;
overflow-x: auto;
      }
  </style>
        </head>
        <body>
  <div class="input-container">
      <input type="text" id="command" placeholder="输入命令">
      <button onclick="sendCommand()">执行</button>
  </div>
  <pre id="output"></pre>

  <h2>创建文件</h2>
  <form method="POST">
      <input type="text" name="filename" placeholder="文件名" required><br>
      <textarea name="content" placeholder="文件内容" rows="10" cols="50" required></textarea><br>
      <button type="submit">创建</button>
  </form>

  <h2>文件下载</h2>
  <ul>
      {{ file_links | safe }}
  </ul>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
  <script>
      const socket = io();
      const output = document.getElementById("output");

      function sendCommand() {
const command = document.getElementById("command").value;
socket.emit("execute_command", { command: command });
      }

      socket.on("command_output", function(data) {
output.textContent += data.output + "\\n";
      });
  </script>
        </body>
        </html>
    """, file_links=file_links)

@socketio.on("execute_command")
def handle_command(data):
    command = data["command"]
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in process.stdout:
        socketio.emit("command_output", {"output": line.strip()})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3000, allow_unsafe_werkzeug=True)
