from .Logger import logger


class Lobby:
    def __init__(self, lobby_id, owner):
        self.id = lobby_id
        self.owner = owner

        self.users = []       # All users currently in the lobby
        self.players = []     # Users that are in the actual players list
        self.started = False  # Whether the game has started

        # Notify about lobby creation
        self.logstr = f'Lobby#{self.id}'
        logger.log(self.logstr, f'Lobby created (owner: {owner.username})')

    def addUser(self, user):
        if user not in self.users:
            self.users.append(user)

        logger.log(self.logstr, 'User joined: ' + user.username)

    def removeUser(self, user, reason):
        if user in self.users:
            self.users.remove(user)

        logger.log(self.logstr, f'User left: {user.username} ({reason})')

    def addAsPlayer(self, user):
        # Can't change players once the game has started
        if self.started:
            return

        # Ensure that the user is in the lobby
        if user in self.users and user not in self.players:
            self.players.append(user)

    def removeAsPlayer(self, user):
        # Can't change players once the game has started
        if self.started:
            return

        # Ensure that the user is in the players list
        if user in self.players:
            self.players.remove(user)

    def shutdown(self, sio, reason):
        logger.log(self.logstr, f'Host {reason}. Shutting down lobby')

        for p in self.users:
            p.lobby = None
            sio.emit('leave_lobby', room=p.sid)

    def setStarted(self):
        self.started = True

    def toJSON(self):
        return {
            'id': self.id,
            'owner_sid': self.owner.sid,
            'users': [u.sid for u in self.users],
            'players': [p.sid for p in self.players],
            'user_usernames': [u.username for u in self.users],
            'player_usernames': [p.username for p in self.players],
            'started': self.started
        }
