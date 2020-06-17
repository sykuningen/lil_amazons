import eventlet
import os
import socketio

from src.Game import Game
from src.Lobby import Lobby
from src.Logger import logger
from src.User import User


# *============================================================= SERVER INIT
static_files = {
    '/':                'pages/index.html',
    '/css/default.css': 'public/css/default.css',
    '/js/ui.js':        'public/js/ui.js',
    '/js/client.js':    'public/js/client.js'}

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=static_files)

port = 8000
if 'PORT' in os.environ.keys():
    port = int(os.environ['PORT'])

# Logging
logger.setSIO(sio)  # Give the logger object direct access to sockets

# Server runtime data
online_users = 0  # TODO: Use lock when accessing this?
users = {}

cur_lobby_id = 0  # TODO: Use lock when accessing this
lobbies = {}
games = {}


# *============================================================= SOCKET.IO
@sio.on('connect')
def connect(sid, env):
    # Create a new user object for this connection
    users[sid] = User(sid)

    # Update global user count
    global online_users
    online_users += 1
    sio.emit('server_stats', {'online_users': online_users})

    # Send client their sid and the lobby listing
    sio.emit('sid', sid, room=sid)
    sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies], room=sid)


@sio.on('disconnect')
def disconnect(sid):
    # Update global user count
    global online_users
    online_users -= 1
    sio.emit('server_stats', {'online_users': online_users})

    # Flag the user as being offline
    users[sid].logOff()

    # Leave the lobby the user was in, if any
    if users[sid].lobby:
        lobby = users[sid].lobby

        # Shut down the lobby if this user owned it and the game hasn't started
        if sid == lobby.owner.sid and not lobby.started:
            lobby.shutdown(sio, 'disconnected')
            del lobbies[lobby.id]

            # Update lobby list for all users
            sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])

        else:
            users[sid].leaveLobby('disconnected')

            # Update the lobby for the other users in it
            for p in lobby.users:
                sio.emit('update_lobby', lobby.toJSON(), room=p.sid)

    logger.removeListener(sid)


@sio.on('login')
def login(sid, data):
    # If the user was connected previously, re-use their old User object.
    #   This allows the player to easily resume games they were in.
    for u in users:
        # TODO: Use some kind of credentials
        if users[u].username == data['username']:
            # Ensure that the user is not still logged in
            if users[u].logged_in:
                return

            users[sid] = users[users[u].sid]
            users[sid].sid = sid  # Change to user's new sid

    users[sid].setUsername(data['username'])
    sio.emit('logged_in', room=sid)


@sio.on('connect_log')
def connectLog(sid):
    if not users[sid].logged_in:
        return

    logger.addListener(sid)
    logger.log('server', f'{users[sid].username} connected to logging server')


# ============================================================== Lobby
@sio.on('create_lobby')
def createLobby(sid):
    # Ensure that user is logged in
    if not users[sid].logged_in:
        return

    # Allow users to create or be in only one lobby at a time
    if users[sid].lobby:
        return

    # Create a new lobby
    global cur_lobby_id
    lobby = Lobby(cur_lobby_id, users[sid])
    cur_lobby_id += 1
    lobbies[lobby.id] = lobby

    users[sid].joinLobby(lobby)

    # Update lobby info for users
    sio.emit('update_lobby', lobby.toJSON(), room=sid)
    sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


@sio.on('join_lobby')
def joinLobby(sid, lobby_id):
    # Ensure that user is logged in
    if not users[sid].logged_in:
        return

    # Don't allow users to enter multiple lobbies at once
    if users[sid].lobby:
        return

    lobby_id = int(lobby_id)

    # Ensure that the lobby exists
    if lobby_id not in lobbies:
        return

    lobby = lobbies[lobby_id]
    users[sid].joinLobby(lobby)

    # Update the lobby for the other users in it
    for p in lobby.users:
        sio.emit('update_lobby', lobby.toJSON(), room=p.sid)


@sio.on('leave_lobby')
def leaveLobby(sid):
    # Leave the lobby the user was in, if any
    if users[sid].lobby:
        lobby = users[sid].lobby

        # Shut down the lobby if this user owned it and the game hasn't started
        if sid == lobby.owner.sid and not lobby.started:
            lobby.shutdown(sio, 'left lobby')
            del lobbies[lobby.id]

            # Update lobby list for all users
            sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])

        else:
            users[sid].leaveLobby('left lobby')
            sio.emit('leave_lobby', lobby.toJSON(), room=sid)

            # Update the lobby for the other users in it
            for p in lobby.users:
                sio.emit('update_lobby', lobby.toJSON(), room=p.sid)


# Join the player list in a lobby (meaning you will be participating)
@sio.on('join_players')
def joinPlayers(sid):
    # Ensure that the user is in a lobby
    if not users[sid].lobby:
        return

    users[sid].lobby.addAsPlayer(users[sid])

    # Update the lobby for the other users in it
    for p in users[sid].lobby.users:
        sio.emit('update_lobby', users[sid].lobby.toJSON(), room=p.sid)

    # Update lobby list for all users
    sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


@sio.on('leave_players')
def leavePlayers(sid):
    # Ensure that the user is in a lobby
    if not users[sid].lobby:
        return

    users[sid].lobby.removeAsPlayer(users[sid])

    # Update the lobby for the other users in it
    for p in users[sid].lobby.users:
        sio.emit('update_lobby', users[sid].lobby.toJSON(), room=p.sid)

    # Update lobby list for all users
    sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


@sio.on('add_ai_player')
def addAiPlayer(sid):
    # Ensure that the user is in a lobby
    if not users[sid].lobby:
        return

    if users[sid].lobby.owner.sid != sid:
        return

    if users[sid].lobby.started:
        return

    ai_player = User(None, ai_player=True)
    users[sid].lobby.addUser(ai_player)
    users[sid].lobby.addAsPlayer(ai_player)

    # Update the lobby for the other users in it
    for p in users[sid].lobby.users:
        sio.emit('update_lobby', users[sid].lobby.toJSON(), room=p.sid)

    # Update lobby list for all users
    sio.emit('lobby_list', [lobbies[x].toJSON() for x in lobbies])


# ============================================================== Game
@sio.on('start_game')
def startGame(sid, game_config):
    # Ensure that the user has permission to start the game
    if not users[sid].lobby:
        return

    if users[sid].lobby.owner.sid != sid:
        return

    if users[sid].lobby.started:
        return

    # Create a new game
    game = Game(sio, users[sid].lobby, game_config)
    games[users[sid].lobby.id] = game

    # Update the lobby for the other users in it
    for p in game.lobby.users:
        sio.emit('update_lobby', game.lobby.toJSON(), room=p.sid)


@sio.on('watch_game')
def watchGame(sid):
    # Ensure that the user is in a lobby
    if not users[sid].lobby:
        return

    lobby_id = users[sid].lobby.id
    if lobby_id in games:
        games[lobby_id].emitBoard(sid)


@sio.on('attempt_move')
def attemptMove(sid, piece, to):
    # Ensure that the user is in a lobby
    if not users[sid].lobby:
        return

    # Ensure that the game has started
    if not users[sid].lobby.started:
        return

    lobby_id = users[sid].lobby.id
    if lobby_id in games:
        games[lobby_id].attemptMove(users[sid], piece, to)


# *============================================================= MAIN
def main():
    eventlet.wsgi.server(eventlet.listen(('', port)), app)


# *============================================================= ENTRYPOINT
if __name__ == '__main__':
    main()
