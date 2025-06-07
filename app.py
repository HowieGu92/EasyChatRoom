from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import secrets
from datetime import datetime
import sys
from flask import send_from_directory
import os
import uuid

CHAT_PASSWORD=""

WebPort = 0
if len(sys.argv) == 3:
    CHAT_PASSWORD=sys.argv[1]
    WebPort=sys.argv[2]
else:
    print("传递参数异常,需要2个参数，第一个是聊天室的密码，第二个是程序需要开放的端口")
    sys.exit(0) 
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['CHAT_PASSWORD'] = CHAT_PASSWORD  # 预设聊天室密码
 
socketio = SocketIO(app, cors_allowed_origins="*")
 
# 存储数据结构
online_users = {}  # {sid: nickname}
message_history = []  # 保存历史消息
 
@app.route('/')
def index():
    return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    nickname = request.form.get('nickname').strip()
    
    if password == app.config['CHAT_PASSWORD'] and nickname:
        if nickname not in online_users.values():
            session['nickname'] = nickname
            session['logged_in'] = True
            return redirect(url_for('chat'))
        return "昵称已被使用，请更换", 403
    return "密码错误或昵称无效", 403
 
@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('chat.html', nickname=session['nickname'])
 
@socketio.on('connect')
def handle_connect():
    if not session.get('logged_in'):
        return False
    
    nickname = session['nickname']
    online_users[request.sid] = nickname
    
    # 广播用户加入
    emit('system_message', {
        'text': f'{nickname} 进入了聊天室',
'time': datetime.now().strftime("%H:%M")
    }, broadcast=True)
    
    # 发送历史消息
    for msg in message_history:
        emit('new_message', msg, room=request.sid)
    
    # 更新在线列表
    emit('update_users', list(online_users.values()), broadcast=True)
 
@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        nickname = online_users.pop(request.sid)
        emit('system_message', {
            'text': f'{nickname} 离开了聊天室',
'time': datetime.now().strftime("%H:%M")
        }, broadcast=True)
        emit('update_users', list(online_users.values()), broadcast=True)
 
@socketio.on('send_message')
def handle_message(data):
    msg = {
        'nickname': session['nickname'],
        'text': data.get('text', ''),
        'images': data.get('images', []),
        'time': datetime.now().strftime("%H:%M")
    }
    message_history.append(msg)
    
    emit('new_message', msg, broadcast=True)

# 图片存储配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return {'error': 'No image'}, 400
    
    file = request.files['image']
    if file.filename == '':
        return {'error': 'Empty filename'}, 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return {'url': f'/images/{filename}'}
    
    return {'error': 'Invalid file type'}, 400

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
 
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',  # 允许所有IP访问
        port=WebPort,
        ssl_context=('server.crt', 'server.key')  # 指定证书
    )