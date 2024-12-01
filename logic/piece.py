class Piece:
    def __init__(self, color, position):
        """
        Base class for all chess pieces.
        :param color: 'white' or 'black'
        :param position: Tuple (row, col) representing the position on the board.
        """
        self.color = color
        self.position = position
        self.has_moved = False # track if a piece has moved (for castling)

    def is_valid_move(self, start, end, board):
        """
        Validate if a move from start to end is valid for this piece.
        To be overridden by specific piece types.
        :param start: Tuple (row, col) starting position.
        :param end: Tuple (row, col) ending position.
        :param board: Board object.
        :return: True if the move is valid, False otherwise.
        """
        raise NotImplementedError("This method should be implemented in derived classes")
