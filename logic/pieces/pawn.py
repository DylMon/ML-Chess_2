from logic.piece import Piece

class Pawn(Piece):
    def is_valid_move(self, start, end, board):
        """
        Validate pawn-specific movement, including en passant capture.
        :param start: Tuple (row, col) starting position.
        :param end: Tuple (row, col) ending position.
        :param board: Board object
        :return: True if the move is valid, False otherwise
        """
        start_row, start_col = start
        end_row, end_col = end
        direction = -1 if self.color == 'white' else 1  # White moves up, black moves down

        # Basic one-step forward move
        if end_col == start_col and end_row == start_row + direction:
            return board.is_empty(end)

        # Two-step forward move
        if end_col == start_col and end_row == start_row + 2 * direction and (start_row == 6 if self.color == 'white' else start_row == 1):
            return board.is_empty(end) and board.is_empty((start_row + direction, start_col))

        # Diagonal capture
        if abs(end_col - start_col) == 1 and end_row == start_row + direction:
            if board.is_opponent_piece(end, self.color):  # Regular capture
                return True

            # En passant capture
            last_move = board.last_move
            if last_move:
                last_start, last_end = last_move
                # Check if the last move was a two-step pawn move and adjacent to the capturing pawn
                if (
                    board.board[last_end[0]][last_end[1]].__class__.__name__ == "Pawn" and
                    abs(last_end[0] - last_start[0]) == 2 and
                    last_end == (start_row, end_col)
                ):
                    return True

        return False

