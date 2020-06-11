class User:
    def __init__(self, sid):
        self.sid = sid
        self.logged_in = False
        self.username = None

        self.lobby = None

    def setUsername(self, username):
        self.username = username
        self.logged_in = True

    def joinLobby(self, lobby):
        self.lobby = lobby
        lobby.addUser(self)

    def leaveLobby(self, reason):
        self.lobby.removeUser(self, reason)
        self.lobby = None

    def logOff(self):
        self.logged_in = False

    def toJSON(self):
        return {
            'sid': self.sid,
            'username': self.username}
