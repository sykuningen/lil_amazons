# Tile meanings
BLANK = -1
BURNED = -2


class AmazonsLogic:
    def validMove(self, board, piece, to):
        # Trying to move to the same tile?
        if piece == to:
            return False

        # Trying to move vertically?
        elif piece['x'] == to['x']:
            bgn = min(piece['y'], to['y'])
            end = max(piece['y'], to['y'])

            if (piece['y'] < to['y']):
                bgn += 1
                end += 1

            for t in range(bgn, end):
                if board.board[piece['x']][t] != BLANK:
                    return False

            return True

        # Trying to move horizontally?
        elif piece['y'] == to['y']:
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
        elif abs(piece['x'] - to['x']) == abs(piece['y'] - to['y']):
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

    def getPieces(self, board, player_n):
        pieces = []

        for x in range(0, board.width):
            for y in range(0, board.height):
                if board.board[x][y] == player_n:
                    pieces.append({'x': x, 'y': y})

        return pieces

    def getValidMoves(self, board, player_n):
        pieces = self.getPieces(board, player_n)
        valid = []

        for x in range(0, board.width):
            for y in range(0, board.height):
                for p in pieces:
                    pos = {'x': x, 'y': y}

                    if pos not in valid and self.validMove(board, p, pos):
                        valid.append(pos)

        return valid

    def regions(self, board):
        regions = {}
        cregion = 0

        tiles_uncheck = []

        for x in range(0, board.width):
            for y in range(0, board.height):
                if board.board[x][y] != BURNED:
                    tiles_uncheck.append({'x': x, 'y': y})

        regions[cregion] = {}
        regions[cregion]['tiles'] = [tiles_uncheck[0]]
        regions[cregion]['owner'] = []

        while True:
            if not tiles_uncheck:
                break

            f = []

            for t1 in regions[cregion]['tiles']:
                for t2 in tiles_uncheck:
                    if abs(t1['x'] - t2['x']) <= 1 and \
                       abs(t1['y'] - t2['y']) <= 1:
                        if t2 not in f:
                            f.append(t2)

            if f:
                for t in f:
                    if t not in regions[cregion]['tiles']:
                        regions[cregion]['tiles'].append(t)

                    tiles_uncheck.remove(t)

                    tile = board.board[t['x']][t['y']]
                    if tile >= 0:
                        regions[cregion]['owner'].append(tile)

            else:
                cregion += 1
                regions[cregion] = {}
                regions[cregion]['tiles'] = [tiles_uncheck[0]]
                regions[cregion]['owner'] = []

        for r in regions:
            owner = regions[r]['owner']

            if len(owner) > 1:
                if all(x == owner[0] for x in owner):
                    regions[r]['owner'] = owner[0]
                else:
                    regions[r]['owner'] = None
            else:
                regions[r]['owner'] = owner[0]

        return regions

    def calculateScores(self, region_info):
        scores = {}

        for r in region_info:
            if region_info[r]['owner'] is not None:
                o = region_info[r]['owner']

                if o in scores:
                    scores[o] += len(region_info[r]['tiles'])
                else:
                    scores[o] = len(region_info[r]['tiles'])

        return scores
