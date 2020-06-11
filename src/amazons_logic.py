# Tile meanings
BLANK = -1
BURNED = -2


class AmazonsLogic:
    def validMove(self, board, piece, to):
        # Trying to move to the same tile?
        if piece == to:
            return False

        # Trying to move horizontally?
        if piece['x'] == to['x']:
            bgn = min(piece['y'], to['y'])
            end = max(piece['y'], to['y'])

            if (piece['y'] < to['y']):
                bgn += 1
                end += 1

            for t in range(bgn, end):
                if board.board[piece['x']][t] != BLANK:
                    return False

            return True

        # Trying to move vertically?
        if piece['y'] == to['y']:
            bgn = min(piece['x'], to['x'])
            end = max(piece['x'], to['x'])

            if (piece['x'] < to['x']):
                bgn += 1
                end += 1

            for t in range(bgn, end):
                if board.board[t][piece['y']] != BLANK:
                    return False

            return True

        # Trying to move diagonally?
        if abs(piece['x'] - to['x']) == abs(piece['y'] - to['y']):
            change_x = 1 if piece['x'] < to['x'] else -1
            change_y = 1 if piece['y'] < to['y'] else -1

            x = piece['x']
            y = piece['y']

            while True:
                x += change_x
                y += change_y

                if board.board[x][y] != BLANK:
                    return False

                if x == to['x']:
                    return True

        return False
