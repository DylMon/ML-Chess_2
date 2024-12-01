from logic.piece import Piece

class Knight(Piece):
    def is_valid_move(self, start, end, board):
        """
        Validate knight-specific movement (L-shaped moves).
        """
        start_row, start_col = start
        end_row, end_col = end

        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)

        # Valid L-shaped moves
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            return board.is_empty(end) or board.is_opponent_piece(end, self.color)

        return False
