from .Logger import logger


class Lobby:
    def __init__(self, lobby_id, owner_sid):
        self.id = lobby_id
        self.owner_sid = owner_sid

        self.users = []
        self.players = []
        self.started = False

        self.logstr = 'Lobby#' + str(self.id)
        logger.log(self.logstr, 'Created')

    def addUser(self, player_sid):
        if player_sid not in self.users:
            self.users.append(player_sid)

        logger.log(self.logstr, 'User joined: ' + str(player_sid))

    def removeUser(self, player_sid, reason):
        if player_sid in self.users:
            self.users.remove(player_sid)

        logger.log(self.logstr, 'User ' + reason + ': ' + str(player_sid))

    def addAsPlayer(self, player_sid):
        if self.started:
            return

        if player_sid in self.users and player_sid not in self.players:
            self.players.append(player_sid)

    def removeAsPlayer(self, player_sid):
        if self.started:
            return

        if player_sid in self.players:
            self.players.remove(player_sid)

    def shutdown(self, sio, users, reason):
        message = 'Host ' + reason + '. Shutting down ('
        message += str(len(self.players)) + ' users affected)'

        logger.log(self.logstr, message)

        for p in self.users:
            users[p]['is_in_lobby'] = False
            sio.emit('leave_lobby', room=p)

    def setStarted(self):
        self.started = True

    def toJSON(self):
        return {
            'id': self.id,
            'owner_sid': self.owner_sid,
            'users': self.users,
            'players': self.players,
            'started': self.started
        }
