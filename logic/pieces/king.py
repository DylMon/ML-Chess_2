from logic.piece import Piece

class King(Piece):
    def is_valid_move(self, start, end, board):
        """
        Validate king-specific movement, including castling.
        """
        start_row, start_col = start
        end_row, end_col = end

        # Standard king movement (one square in any direction)
        if abs(end_row - start_row) <= 1 and abs(end_col - start_col) <= 1:
            return board.is_empty(end) or board.is_opponent_piece(end, self.color)

        # Castling move (two squares left or right)
        if not self.has_moved and start_row == end_row and abs(end_col - start_col) == 2:
            # Determine the direction of castling
            rook_col = 0 if end_col < start_col else 7  # Rook on left (queen-side) or right (king-side)
            rook = board.board[start_row][rook_col]

            # Ensure the rook is valid and hasn't moved
            if not rook or rook.has_moved or rook.__class__.__name__ != "Rook" or rook.color != self.color:
                return False

            # Ensure all squares between king and rook are empty
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, rook_col, step):
                if not board.is_empty((start_row, col)):
                    return False

            # Ensure the king is not in check, and does not pass through or end in check
            for col in range(start_col, end_col + step, step):
                if board.is_under_attack((start_row, col), self.color):
                    return False

            return True

        return False
