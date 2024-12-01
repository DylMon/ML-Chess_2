from logic.piece import Piece

class Queen(Piece):
    def is_valid_move(self, start, end, board):
        """
        Validate queen-specific movement (combines rook and bishop movement).
        """
        start_row, start_col = start
        end_row, end_col = end

        # Rook-like movement (horizontal or vertical)
        if start_row == end_row or start_col == end_col:
            step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        # Bishop-like movement (diagonal)
        elif abs(end_row - start_row) == abs(end_col - start_col):
            step_row = 1 if end_row > start_row else -1
            step_col = 1 if end_col > start_col else -1
        else:
            return False

        # Check for obstacles in the path
        current_row, current_col = start_row + step_row, start_col + step_col
        while (current_row, current_col) != (end_row, end_col):
            if not board.is_empty((current_row, current_col)):
                return False
            current_row += step_row
            current_col += step_col

        # Final destination must be empty or occupied by opponent
        return board.is_empty(end) or board.is_opponent_piece(end, self.color)
