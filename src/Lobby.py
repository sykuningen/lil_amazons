class Lobby:
    def __init__(self, lobby_id, owner_sid):
        self.id = lobby_id
        self.owner_sid = owner_sid

        self.players = []
        self.started = False

    def addPlayer(self, player_sid):
        self.players.append(player_sid)

    def setStarted(self):
        self.started = True

    def toJSON(self):
        return {
            'id': self.id,
            'owner_sid': self.owner_sid,
            'players': self.players,
            'started': self.started
        }
