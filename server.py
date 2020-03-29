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
users = {}

cur_lobby_id = 0  # TODO: Use lock when accessing this
lobbies = {}


# *============================================================= SOCKET.IO
@sio.on('connect')
def connect(sid, env):
    print(f'Connection from SID {sid}')

    users[sid] = {
        'is_in_lobby':    False,
        'in_lobby':       0,
        'is_lobby_owner': False
    }

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

    # Leave the lobby the user was in, if any
    if users[sid]['is_in_lobby']:
        lobby = lobbies[users[sid]['in_lobby']]

        # Shut down the lobby if this user owned it
        if users[sid]['is_lobby_owner']:
            for p in lobby.players:
                users[p]['is_in_lobby'] = False
                sio.emit('leave_lobby', room=p)

            del lobbies[users[sid]['in_lobby']]

        else:
            lobby.players.remove(sid)

            # Update the lobby for the other users in it
            for p in lobby.players:
                sio.emit('update_lobby', lobby.toJSON(), room=p)

        # Update lobby list for all users
        sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


# Lobby
@sio.on('create_lobby')
def createLobby(sid):
    # Allow users to create or be in only one lobby at a time
    if not users[sid]['is_in_lobby']:
        global cur_lobby_id
        lobby = Lobby(cur_lobby_id, sid)
        cur_lobby_id += 1
        lobbies[lobby.id] = lobby

        users[sid]['is_in_lobby'] = True
        users[sid]['in_lobby'] = lobby.id
        users[sid]['is_lobby_owner'] = True

        lobby.addPlayer(sid)
        sio.emit('update_lobby', lobby.toJSON(), room=sid)

        # Update lobby list for all users
        sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


@sio.on('join_lobby')
def joinLobby(sid, lobby_id):
    # Don't allow users to enter multiple lobbies at once
    if users[sid]['is_in_lobby']:
        return

    lobby_id = int(lobby_id)

    if lobby_id in lobbies:
        lobby = lobbies[lobby_id]

        if sid not in lobby.players:
            lobby.addPlayer(sid)

            users[sid]['is_in_lobby'] = True
            users[sid]['in_lobby'] = lobby.id
            users[sid]['is_lobby_owner'] = False

            # Update the lobby for the other users in it
            for p in lobby.players:
                sio.emit('update_lobby', lobby.toJSON(), room=p)

            # Update lobby list for all users
            sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


# *============================================================= MAIN
def main():
    eventlet.wsgi.server(eventlet.listen(('', port)), app)


# *============================================================= ENTRYPOINT
if __name__ == '__main__':
    main()
