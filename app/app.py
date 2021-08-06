from flask import Flask, render_template, request
import socket, json
from flask_socketio import SocketIO,emit
app = Flask(__name__)

socketio = SocketIO(app)
# === socket ===
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('tracking')
def tracking(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error:", e)
        return json.dumps({"error": "establish error"})

    try:
        sock.connect(("127.0.0.1", 8062))
        sock.settimeout(1)
        # sock.setblocking(False)
        result = []
        receive_message = sock.recv(65536)
        # result = receive_message
        result.append(receive_message)
        while (len(receive_message) > 0):
            receive_message = sock.recv(65536)
            result.append(receive_message)
        result = b''.join(result)
        # print('result length', len(result))
        emit('send_track', result)
    except BlockingIOError as e:
        # print("BlockingIOError: ", e)
        pass    
    except socket.error as e:
        print("[ERROR] ", e)
        return json.dumps({"error": "connect error"})
    
    # print('===receive_message====',receive_message)
    
    sock.close()
    # return json.dumps(receive_message)
# ===========

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view.html")
def view():
    return render_template("view.html")


@app.route("/start_camera")
def start_control():
    print("=== start control ===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error:", e)
        return json.dumps({"error": "establish error"})

    try:
        sock.connect(("127.0.0.1", 8060))
    except socket.error as e:
        print("[ERROR] ", e)
        return json.dumps({"error": "connect error"})

    message = '{"message":"start_camera"}'
    sock.send(message.encode("UTF-8"))
    receive_message = sock.recv(1024).decode("utf-8")
    receive_dict = json.loads(receive_message)
    sock.close()
    return json.dumps(receive_dict)


@app.route("/stop_camera")
def stop_control():
    print("===stop capture===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error:", e)
        return json.dumps({"error": "establish error"})

    try:
        sock.connect(("127.0.0.1", 8060))
    except socket.error as e:
        print("[ERROR] ", e)
        return json.dumps({"error": "connect error"})

    message = '{"message":"stop_camera"}'
    sock.send(message.encode("UTF-8"))
    receive_message = sock.recv(1024).decode("utf-8")
    receive_dict = json.loads(receive_message)
    sock.close()
    return json.dumps(receive_dict)



@app.route("/start_preview")
def start_redis():
    print("=== start preview ===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error:", e)
        return json.dumps({"error": "establish error"})

    try:
        sock.connect(("127.0.0.1", 8060))
    except socket.error as e:
        print("[ERROR] ", e)
        return json.dumps({"error": "connect error"})

    message = '{"message":"start_preview"}'
    sock.send(message.encode("UTF-8"))
    receive_message = sock.recv(1024).decode("utf-8")
    receive_dict = json.loads(receive_message)
    sock.close()
    return json.dumps(receive_dict)

@app.route("/submit_change", methods=['POST','GET'])
def submit_change():
    print("=== submit_change ===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error:", e)
        return json.dumps({"error": "establish error"})

    try:
        sock.connect(("127.0.0.1", 8060))
    except socket.error as e:
        print("[ERROR] ", e)
        return json.dumps({"error": "connect error"})
        
    req =  request.get_json()
    message = {"message":"submit_change", "data":req}
    message = json.dumps(message)
    sock.send(message.encode("UTF-8"))
    receive_message = sock.recv(1024).decode("utf-8")
    receive_dict = json.loads(receive_message)
    sock.close()
    return json.dumps(receive_dict)




if __name__ == "__main__":
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.debug = True
    # app.run(host="127.0.0.1", port=5001)
    socketio.run(app, host="127.0.0.1", port=5001)
