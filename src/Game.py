class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.board = [[0 for x in range(width)] for y in range(height)]

    def toJSON(self):
        return {
            'width': self.width,
            'height': self.height,
            'board': self.board
        }


class Game:
    def __init__(self, sio, lobby):
        self.sio = sio

        self.lobby = lobby
        self.id = lobby.id

        self.lobby.setStarted()
        print('Game ID#' + str(self.id) + ' started')

        # Initialize the game board
        self.board = Board(10, 10)

        for p in self.lobby.players:
            sio.emit('game_data', self.toJSON(), room=p)

    def toJSON(self):
        return {
            'id': self.id,
            'lobby': self.lobby.toJSON(),
            'board': self.board.toJSON()
        }
