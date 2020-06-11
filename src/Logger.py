class Logger:
    def __init__(self):
        self.listeners = []
        self.messages = []

    def setSIO(self, sio):
        self.sio = sio

    def addListener(self, sid):
        if sid not in self.listeners:
            self.listeners.append(sid)

    def removeListener(self, sid):
        if sid in self.listeners:
            self.listeners.remove(sid)

    def log(self, sender, message):
        new_msg = {
            'sender': sender,
            'message': message
        }

        self.messages.append(new_msg)

        for l in self.listeners:
            self.sio.emit('log_message', new_msg, room=l)


logger = Logger()
