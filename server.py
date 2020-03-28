import eventlet
import socketio


# *============================================================= SERVER INIT
static_files = {
    '/': 'pages/index.html',
    '/css/default.css': 'public/css/default.css',
    '/js/client.js': 'public/js/client.js'
}

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=static_files)

port = 8000


# *============================================================= SOCKET.IO
@sio.on('connect')
def connect(sid, env):
    print(f'Connection from SID {sid}')


@sio.on('disconnect')
def disconnect(sid):
    print(f'Disconnection from SID {sid}')


# *============================================================= MAIN
def main():
    eventlet.wsgi.server(eventlet.listen(('', port)), app)


# *============================================================= ENTRYPOINT
if __name__ == '__main__':
    main()
