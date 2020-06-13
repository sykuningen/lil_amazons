from .Logger import logger
from .amazons_logic import AmazonsLogic


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
            pass  # TODO: Dispatch an error

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
        self.id = lobby.id  # Game IDs match their associated lobby ID

        # Initialize the game board
        self.board = Board(10, 10)
        self.current_player = 0
        self.lmp = None       # Last moved piece
        self.burning = False  # Does current player have to burn a tile now?

        # Initialize game pieces
        self.board.placePiece(0, (0, 0))
        self.board.placePiece(1, (9, 9))

        # Finalize setup
        self.lobby.setStarted()
        self.emitBoard()

        # Notify about game start
        self.logstr = f'Game#{str(self.id)}'
        player_list = str([p.username for p in lobby.players])
        logger.log(self.logstr, f'Game started (players: {player_list})')

    def attemptMove(self, player, piece, to):
        if self.burning:
            self.attemptBurn(player, to)
            return

        try:
            if player not in self.lobby.players:
                return  # This user isn't in this game

            player_n = self.lobby.players.index(player)
            piece_tile = self.board.board[piece['x']][piece['y']]

            if self.current_player != player_n:
                return  # It isn't this player's turn
            if piece['x'] < 0 or piece['y'] < 0:
                return  # Prevent weird list indexing
            if piece_tile != player_n:
                return  # No piece here, or piece belongs to another player
            if not AmazonsLogic().validMove(self.board, piece, to):
                return  # This isn't a valid move

            # Move the piece
            self.board.board[to['x']][to['y']] = piece_tile
            self.board.board[piece['x']][piece['y']] = BLANK

            self.lmp = {'x': to['x'], 'y': to['y']}
            self.burning = True  # Player must now burn a tile

            self.emitBoard()
            self.sio.emit('select_piece', self.lmp, player.sid)

        except IndexError:
            pass  # TODO: Dispatch an error

    def attemptBurn(self, player, to):
        try:
            player_n = self.lobby.players.index(player)

            if player not in self.lobby.players:
                return  # This user isn't in this game
            if self.current_player != player_n:
                return  # It isn't this player's turn
            if not AmazonsLogic().validMove(self.board, self.lmp, to):
                return  # This isn't a valid burn

            self.board.board[to['x']][to['y']] = BURNED

            # Next player's turn
            self.burning = False

            self.current_player += 1
            if self.current_player == len(self.lobby.players):
                self.current_player = 0

            self.emitBoard()
            self.sio.emit('select_piece', {'x': -1, 'y': -1}, player.sid)

        except IndexError:
            pass  # TODO: Dispatch an error

    def toJSON(self):
        return {
            'id': self.id,
            'lobby': self.lobby.toJSON(),
            'board': self.board.toJSON(),
            'current_player': self.current_player,
            'lmp': self.lmp,
            'burning': self.burning
        }

    def emitBoard(self, to=None):
        if to:
            self.sio.emit('game_data', self.toJSON(), room=to)
        else:
            for p in self.lobby.users:
                self.sio.emit('game_data', self.toJSON(), room=p.sid)
