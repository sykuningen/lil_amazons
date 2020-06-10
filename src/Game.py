# Tile meanings
BLANK = -1
BURNED = -2


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.board = [[BLANK for y in range(height)] for x in range(width)]

    def placePiece(self, player_n, pos):
        try:
            x, y = pos
            self.board[x][y] = player_n

        except IndexError:
            pass

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
        self.current_player = 0

        # Initialize game pieces
        self.board.placePiece(0, (0, 0))
        self.board.placePiece(1, (9, 9))

        self.emitBoard()

    def attemptMove(self, player_sid, piece, to):
        if player_sid not in self.lobby.players:
            return

        if piece['x'] < 0 or piece['y'] < 0:
            return

        try:
            piece_tile = self.board.board[piece['x']][piece['y']]

            # Ensure that a piece exists at the given position
            if piece_tile >= 0:
                self.board.board[to['x']][to['y']] = piece_tile
                self.board.board[piece['x']][piece['y']] = BLANK

            self.emitBoard()

        except IndexError:
            pass

    def toJSON(self):
        return {
            'id': self.id,
            'lobby': self.lobby.toJSON(),
            'board': self.board.toJSON()
        }

    def emitBoard(self):
        for p in self.lobby.players:
            self.sio.emit('game_data', self.toJSON(), room=p)
