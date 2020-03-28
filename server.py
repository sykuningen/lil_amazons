import eventlet
import socketio


# *============================================================= SERVER INIT
static_files = {
    '/':                'pages/index.html',
    '/css/default.css': 'public/css/default.css',
    '/js/ui.js':        'public/js/ui.js',
    '/js/client.js':    'public/js/client.js'
}

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=static_files)

port = 8000

# Server runtime data
online_users = 0


# *============================================================= SOCKET.IO
@sio.on('connect')
def connect(sid, env):
    print(f'Connection from SID {sid}')

    global online_users
    online_users += 1
    sio.emit('server_stats', {
        'online_users': online_users
    })


@sio.on('disconnect')
def disconnect(sid):
    print(f'Disconnection from SID {sid}')

    global online_users
    online_users -= 1
    sio.emit('server_stats', {
        'online_users': online_users
    })


# *============================================================= MAIN
def main():
    eventlet.wsgi.server(eventlet.listen(('', port)), app)


# *============================================================= ENTRYPOINT
if __name__ == '__main__':
    main()
