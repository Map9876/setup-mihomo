import os
import subprocess
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template_string("""
        <h1>命令执行器</h1>
        <input type="text" id="command" placeholder="输入命令">
        <button onclick="sendCommand()">执行</button>
        <pre id="output"></pre>
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
    """)

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
