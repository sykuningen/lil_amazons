import eventlet
import socketio

from src.Lobby import Lobby


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

lobbies = {}
cur_lobby_id = 0  # TODO: Use lock when accessing this


# *============================================================= SOCKET.IO
@sio.on('connect')
def connect(sid, env):
    print(f'Connection from SID {sid}')

    global online_users
    online_users += 1
    sio.emit('server_stats', {
        'online_users': online_users
    })

    sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies], room=sid)


@sio.on('disconnect')
def disconnect(sid):
    print(f'Disconnection from SID {sid}')

    global online_users
    online_users -= 1
    sio.emit('server_stats', {
        'online_users': online_users
    })

    # Shutdown any lobbies the user created
    if sid in lobbies:
        del lobbies[sid]


# Lobby
@sio.on('create_lobby')
def createLobby(sid):
    if sid not in lobbies:  # Allow users to create only one lobby at a time
        global cur_lobby_id
        lobby = lobbies[sid] = Lobby(cur_lobby_id, sid)
        cur_lobby_id += 1

        lobby.addPlayer(sid)
        sio.emit('join_lobby', lobby.toJSON(), room=sid)

        # Update lobby list for all users
        sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


# *============================================================= MAIN
def main():
    eventlet.wsgi.server(eventlet.listen(('', port)), app)


# *============================================================= ENTRYPOINT
if __name__ == '__main__':
    main()
