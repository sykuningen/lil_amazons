class Lobby:
    def __init__(self, lobby_id, owner_sid):
        self.id = lobby_id
        self.owner_sid = owner_sid

        self.players = []

    def addPlayer(self, player_sid):
        self.players.append(player_sid)

    def toJSON(self):
        return {
            'id': self.id,
            'owner_sid': self.owner_sid,
            'players': self.players
        }
