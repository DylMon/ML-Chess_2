from logic.piece import Piece

class Bishop(Piece):
    def is_valid_move(self, start, end, board):
        """
        Validate bishop-specific movement (diagonal).
        """
        start_row, start_col = start
        end_row, end_col = end

        # Must move diagonally
        if abs(end_row - start_row) == abs(end_col - start_col):
            step_row = 1 if end_row > start_row else -1
            step_col = 1 if end_col > start_col else -1

            # Check for obstacles in the path
            current_row, current_col = start_row + step_row, start_col + step_col
            while (current_row, current_col) != (end_row, end_col):
                if not board.is_empty((current_row, current_col)):
                    return False
                current_row += step_row
                current_col += step_col

            # Final destination must be empty or occupied by opponent
            return board.is_empty(end) or board.is_opponent_piece(end, self.color)

        return False
