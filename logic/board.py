from logic.pieces.pawn import Pawn
from logic.pieces.rook import Rook
from logic.pieces.knight import Knight
from logic.pieces.bishop import Bishop
from logic.pieces.queen import Queen
from logic.pieces.king import King  # Add this line

class Board:
    def __init__(self):
        """
        Initialize the chessboard with the starting position.
        """
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board with None
        self.initialize_pieces()
        self.current_turn = "white"  # White starts first
        self.last_move = None

    def initialize_pieces(self):
        """
        Set up the board with white pieces at the bottom (rows 6-7) and black pieces at the top (rows 0-1).
        """
        from logic.pieces.pawn import Pawn
        from logic.pieces.rook import Rook
        from logic.pieces.knight import Knight
        from logic.pieces.bishop import Bishop
        from logic.pieces.queen import Queen
        from logic.pieces.king import King

        # Pawns
        for col in range(8):
            self.board[6][col] = Pawn('white', (6, col))  # White pawns on row 6
            self.board[1][col] = Pawn('black', (1, col))  # Black pawns on row 1

        # Rooks
        self.board[7][0] = Rook('white', (7, 0))
        self.board[7][7] = Rook('white', (7, 7))
        self.board[0][0] = Rook('black', (0, 0))
        self.board[0][7] = Rook('black', (0, 7))

        # Knights
        self.board[7][1] = Knight('white', (7, 1))
        self.board[7][6] = Knight('white', (7, 6))
        self.board[0][1] = Knight('black', (0, 1))
        self.board[0][6] = Knight('black', (0, 6))

        # Bishops
        self.board[7][2] = Bishop('white', (7, 2))
        self.board[7][5] = Bishop('white', (7, 5))
        self.board[0][2] = Bishop('black', (0, 2))
        self.board[0][5] = Bishop('black', (0, 5))

        # Queens
        self.board[7][3] = Queen('white', (7, 3))  # White queen on bottom row
        self.board[0][3] = Queen('black', (0, 3))  # Black queen on top row

        # Kings
        self.board[7][4] = King('white', (7, 4))  # White king on bottom row
        self.board[0][4] = King('black', (0, 4))  # Black king on top row

    def move_piece(self, start, end):
        """
        Move a piece from start to end position, if valid.
        :param start: Tuple (row, col) starting position.
        :param end: Tuple (row, col) ending position.
        :return: True if the move was successful, False otherwise.
        """
        piece = self.board[start[0]][start[1]]
        if piece and piece.is_valid_move(start, end, self):
            # Handle special moves
            if isinstance(piece, King) and abs(end[1] - start[1]) == 2:  # Castling
                self._handle_castling(start, end, piece)
            elif isinstance(piece, Pawn) and abs(start[1] - end[1]) == 1 and self.is_empty(end):  # En passant
                self._handle_en_passant(start, end, piece)

            # Perform the move
            self.board[end[0]][end[1]] = piece
            self.board[start[0]][start[1]] = None
            piece.position = end
            piece.has_moved = True
            self.last_move = (start, end)  # Update last move

            # Handle pawn promotion
            if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
                self._handle_pawn_promotion(end, piece)

            # Check if the opponent's king is in check or checkmate
            opponent_color = "black" if piece.color == "white" else "white"
            if self.is_in_check(opponent_color):
                print(f"{opponent_color.capitalize()} is in check!")
                if self.is_checkmate(opponent_color):
                    print(f"{opponent_color.capitalize()} is in checkmate! {piece.color.capitalize()} wins!")

            return True
        return False

    def _handle_castling(self, start, end, king):
        """
        Handle castling logic.
        """
        if end[1] > start[1]:  # Kingside castling
            rook_start_col = 7
            rook_end_col = end[1] - 1
            print(f"{king.color.capitalize()} performed kingside castling.")
        else:  # Queenside castling
            rook_start_col = 0
            rook_end_col = end[1] + 1
            print(f"{king.color.capitalize()} performed queenside castling.")

        # Move the rook
        rook = self.board[start[0]][rook_start_col]
        self.board[start[0]][rook_end_col] = rook
        self.board[start[0]][rook_start_col] = None
        rook.position = (start[0], rook_end_col)
        rook.has_moved = True

    def _handle_en_passant(self, start, end, pawn):
        """
        Handle en passant logic.
        """
        captured_pawn_row = start[0]
        captured_pawn_col = end[1]
        self.board[captured_pawn_row][captured_pawn_col] = None  # Remove the captured pawn
        print(f"{pawn.color.capitalize()} performed en passant.")

    def _handle_pawn_promotion(self, end, pawn):
        """
        Handle pawn promotion logic. Automatically promote to a queen for simplicity.
        """
        from logic.pieces.queen import Queen
        self.board[end[0]][end[1]] = Queen(pawn.color, end)  # Replace the pawn with a queen
        print(f"{pawn.color.capitalize()} promoted a pawn to a queen at {end}.")

    def is_in_check(self, color):
        """
        Determine if the king of the given color is in check.
        :param color: 'white' or 'black'
        :return: True if the king is in check, False otherwise
        """
        # Find the king's position
        king_position = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.__class__.__name__ == "King" and piece.color == color:
                    king_position = (row, col)
                    break  # Exit the inner loop when the king is found
            if king_position:  # Exit the outer loop if the king is found
                break
        else:  # Executes only if the king is not found after checking the entire board
            raise ValueError(f"No king found for color {color}")

        # Check if any opponent piece can attack the king's position
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color and piece.is_valid_move((row, col), king_position, self):
                    return True

        return False

    def is_checkmate(self, color):
        """
        Determine if the given color is in checkmate.
        :param color: 'white' or 'black'
        :return: True if the color is in checkmate, False otherwise
        """
        if not self.is_in_check(color):
            return False

        # Check if any legal move can remove the threat
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if piece.is_valid_move((start_row, start_col), (end_row, end_col), self):
                                # Simulate the move
                                captured_piece = self.board[end_row][end_col]
                                self.board[end_row][end_col] = piece
                                self.board[start_row][start_col] = None

                                if not self.is_in_check(color):  # If move resolves the check
                                    # Undo the simulated move
                                    self.board[start_row][start_col] = piece
                                    self.board[end_row][end_col] = captured_piece
                                    return False

                                # Undo the simulated move
                                self.board[start_row][start_col] = piece
                                self.board[end_row][end_col] = captured_piece

        return True

    def is_legal_move(self, start, end, color):
        """
        Determine if a move is legal, ensuring it does not leave the king in check.
        :param start: Tuple (row, col) starting position.
        :param end: Tuple (row, col) ending position.
        :param color: 'white' or 'black' indicating the player's color.
        :return: True if the move is legal, False otherwise.
        """
        # Get the piece being moved
        piece = self.board[start[0]][start[1]]

        # Basic checks: is there a piece, and does it belong to the current player?
        if not piece or piece.color != color:
            return False

        # Check if the move is valid for the piece itself
        if not piece.is_valid_move(start, end, self):  # Uses `is_valid_move` in `piece.py`
            return False

        # Simulate the move
        captured_piece = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None
        piece.position = end

        # Check if the king is still in check
        king_in_check = self.is_in_check(color)

        # Undo the simulated move
        self.board[start[0]][start[1]] = piece
        self.board[end[0]][end[1]] = captured_piece
        piece.position = start

        return not king_in_check

    def toggle_turn(self):
        """
        Toggle the current turn between 'white' and 'black'.
        """
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def is_empty(self, position):
        """
        Check if a position on the board is empty.
        :param position: Tuple (row, col)
        :return: True if the position is empty, False otherwise
        """
        row, col = position
        return self.board[row][col] is None

    def is_opponent_piece(self, position, color):
        """
        Check if a position is occupied by an opponent's piece.
        :param position: Tuple (row, col)
        :param color: The current player's color
        :return: True if an opponent's piece occupies the position, False otherwise
        """
        row, col = position
        piece = self.board[row][col]
        return piece is not None and piece.color != color

    def is_under_attack(self, position, color):
        """
        Check if a position is under attack by opponent pieces.
        :param position: Tuple (row, col)
        :param color: Current player's color
        :return: True if the position is under attack, False otherwise
        """
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color and piece.is_valid_move((row, col), position, self):
                    return True
        return False
