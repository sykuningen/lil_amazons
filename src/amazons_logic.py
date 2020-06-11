class AmazonsLogic:
    def validMove(self, board, piece, to):
        # Trying to move to the same tile?
        if piece == to:
            return False

        # Trying to move horizontally?
        if piece['x'] == to['x']:
            return True

        # Trying to move vertically?
        if piece['y'] == to['y']:
            return True

        # Trying to move diagonally?
        if abs(piece['x'] - to['x']) == abs(piece['y'] - to['y']):
            return True
