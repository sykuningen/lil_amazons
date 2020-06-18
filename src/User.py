class User:
    def __init__(self, sid, ai_player=False):
        self.sid = sid
        self.logged_in = False
        self.username = None

        self.lobby = None

        # AI
        self.ai_player = ai_player

        if ai_player:
            self.username = 'AI Player'

    def setUsername(self, username):
        self.username = username
        self.logged_in = True

    def joinLobby(self, lobby):
        self.lobby = lobby
        lobby.addUser(self)

    def leaveLobby(self, reason):
        lobby = self.lobby

        self.lobby.removeUser(self, reason)
        self.lobby = None

        return lobby

    def logOff(self):
        self.logged_in = False

    def toJSON(self):
        return {
            'sid': self.sid,
            'username': self.username}
