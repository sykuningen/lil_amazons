from .Logger import logger


class Lobby:
    def __init__(self, lobby_id, owner_sid):
        self.id = lobby_id
        self.owner_sid = owner_sid

        self.players = []
        self.started = False

        self.logstr = 'Lobby#' + str(self.id)
        logger.log(self.logstr, 'Created')

    def addPlayer(self, player_sid):
        self.players.append(player_sid)
        logger.log(self.logstr, 'User joined: ' + str(player_sid))

    def removePlayer(self, player_sid, reason):
        self.players.remove(player_sid)
        logger.log(self.logstr, 'User ' + reason + ': ' + str(player_sid))

    def shutdown(self, sio, users, reason):
        message = 'Host ' + reason + '. Shutting down ('
        message += str(len(self.players)) + ' users affected)'

        logger.log(self.logstr, message)

        for p in self.players:
            users[p]['is_in_lobby'] = False
            sio.emit('leave_lobby', room=p)

    def setStarted(self):
        self.started = True

    def toJSON(self):
        return {
            'id': self.id,
            'owner_sid': self.owner_sid,
            'players': self.players,
            'started': self.started
        }
