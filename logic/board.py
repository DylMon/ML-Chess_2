from logic.pieces.pawn import Pawn
from logic.pieces.rook import Rook
from logic.pieces.knight import Knight
from logic.pieces.bishop import Bishop
from logic.pieces.queen import Queen
from logic.pieces.king import King  # Add this line
import random
import tensorflow as tf
import os
import numpy as np

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.initialize_pieces()
        self.current_turn = "white"
        self.last_move = None
        self.model = self.load_model()  # Load the trained model

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
        print(f"Attempting move: {self.current_turn.capitalize()} from {start} to {end}")

        piece = self.board[start[0]][start[1]]
        if not piece or piece.color != self.current_turn:
            print(f"Invalid move: It's {self.current_turn.capitalize()}'s turn.")
            return False

        # Handle castling
        if isinstance(piece, King) and abs(end[1] - start[1]) == 2:  # Castling move
            if self._handle_castling(start, end, piece):
                self.toggle_turn()
                return True

        # Handle en passant
        if isinstance(piece, Pawn) and abs(start[1] - end[1]) == 1 and self.is_empty(end):
            last_move = self.last_move
            if last_move:
                last_start, last_end = last_move
                captured_pawn = self.board[last_end[0]][last_end[1]]
                if (
                        captured_pawn and
                        captured_pawn.__class__.__name__ == "Pawn" and
                        abs(last_end[0] - last_start[0]) == 2 and
                        last_end == (start[0], end[1])
                ):
                    # Simulate en passant
                    self.board[end[0]][end[1]] = piece
                    self.board[start[0]][start[1]] = None
                    self.board[last_end[0]][last_end[1]] = None  # Remove the captured pawn
                    piece.position = end
                    self.last_move = (start, end)

                    # Check if the king is still in check
                    if self.is_in_check(self.current_turn):
                        print(f"Invalid move: {self.current_turn.capitalize()} is still in check!")
                        # Undo the move
                        self.board[start[0]][start[1]] = piece
                        self.board[end[0]][end[1]] = None
                        self.board[last_end[0]][last_end[1]] = captured_pawn
                        piece.position = start
                        return False

                    print(f"{self.current_turn.capitalize()} performed en passant.")
                    self.toggle_turn()
                    return True

        # Standard move
        if not self.is_legal_move(start, end, self.current_turn):
            print(f"Invalid move: {self.current_turn.capitalize()} cannot make this move.")
            return False

        # Perform the move
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None
        piece.position = end
        piece.has_moved = True
        self.last_move = (start, end)
        print(f"{self.current_turn.capitalize()} moved {piece.__class__.__name__} to {end}")

        # Handle pawn promotion
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            self._handle_pawn_promotion(end, piece)

        # Check if the move resolved the check
        if self.is_in_check(self.current_turn):
            print(f"Invalid move: {self.current_turn.capitalize()} is still in check!")
            # Undo the move
            self.board[start[0]][start[1]] = piece
            self.board[end[0]][end[1]] = None
            piece.position = start
            return False

        # Check if the opponent's king is in check or checkmate
        opponent_color = "black" if piece.color == "white" else "white"
        if self.is_in_check(opponent_color):
            print(f"{opponent_color.capitalize()} is in check!")
            if self.is_checkmate(opponent_color):
                print(f"{opponent_color.capitalize()} is in checkmate! {piece.color.capitalize()} wins!")

        # Toggle the turn only for valid moves
        self.toggle_turn()
        return True

    def _handle_castling(self, start, end, king):
        """
        Handle castling logic.
        """
        rook_start_col = 0 if end[1] < start[1] else 7  # Determine kingside or queenside
        rook_end_col = end[1] - 1 if end[1] > start[1] else end[1] + 1

        # Ensure the rook exists and is in the correct position
        rook = self.board[start[0]][rook_start_col]
        if not rook or rook.color != king.color or rook.__class__.__name__ != "Rook":
            print("Invalid castling: Rook not found or in the wrong position.")
            return False

        # Move the rook
        self.board[start[0]][rook_end_col] = rook
        self.board[start[0]][rook_start_col] = None
        rook.position = (start[0], rook_end_col)
        rook.has_moved = True

        # Move the king
        self.board[end[0]][end[1]] = king
        self.board[start[0]][start[1]] = None
        king.position = end
        king.has_moved = True

        print(f"{king.color.capitalize()} performed {'kingside' if end[1] > start[1] else 'queenside'} castling.")
        return True

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
        piece = self.board[start[0]][start[1]]
        if not piece or piece.color != color:
            print(f"Illegal move: No valid piece at {start} for {color}.")
            return False

        if not piece.is_valid_move(start, end, self):
            print(f"Illegal move: {piece.__class__.__name__} cannot move from {start} to {end}.")
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

        if king_in_check:
            print(f"Illegal move: {color.capitalize()} would still be in check after this move.")
        return not king_in_check

    def toggle_turn(self):
        """
        Toggle the current turn between 'white' and 'black'.
        """
        self.current_turn = "black" if self.current_turn == "white" else "white"
        print(f"Turn toggled. It's now {self.current_turn}'s turn.")  # Debugging

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

    def load_model(self):
        """
        Load the trained neural network model.
        """
        model_path = os.path.join(os.path.dirname(__file__), "../ai/chess_model.h5")
        try:
            model = tf.keras.models.load_model(model_path)
            print("Model loaded successfully.")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def fen_to_matrix(self, fen):
        """
        Convert FEN string into an 8x8x12 matrix for model input.
        """
        import chess  # Import chess module for FEN parsing
        board = chess.Board(fen)
        matrix = np.zeros((8, 8, 12), dtype=int)

        piece_to_channel = {
            'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
            'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)
                matrix[row, col, piece_to_channel[piece.symbol()]] = 1

        return matrix

    def make_ai_move(self):
        """
        AI logic for Black using the trained neural network.
        """
        if not self.model:
            print("AI cannot play: Model not loaded.")
            return False

        legal_moves = []
        move_scores = []

        # Generate all legal moves for Black
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece.color == "black":
                    for end_row in range(8):
                        for end_col in range(8):
                            if piece.is_valid_move((start_row, start_col), (end_row, end_col), self):
                                if self.is_legal_move((start_row, start_col), (end_row, end_col), "black"):
                                    legal_moves.append(((start_row, start_col), (end_row, end_col)))

        if not legal_moves:
            if self.is_in_check("black"):
                print("Black is in checkmate! White wins!")
            else:
                print("Stalemate! The game is a draw.")
            return False

        # Evaluate all legal moves
        for move in legal_moves:
            start, end = move

            # Simulate the move
            piece = self.board[start[0]][start[1]]
            captured_piece = self.board[end[0]][end[1]]
            self.board[end[0]][end[1]] = piece
            self.board[start[0]][start[1]] = None
            piece.position = end

            # Convert the board to FEN and predict the score
            fen = self.get_fen()  # Method to get the current board's FEN string
            board_matrix = self.fen_to_matrix(fen)
            score = self.model.predict(board_matrix[np.newaxis, ...])[0][0]  # Predict score
            move_scores.append(score)

            # Undo the move
            self.board[start[0]][start[1]] = piece
            self.board[end[0]][end[1]] = captured_piece
            piece.position = start

        # Select the move with the highest score
        best_move_idx = np.argmax(move_scores)
        best_move = legal_moves[best_move_idx]
        print(f"AI selects move: {best_move} with score {move_scores[best_move_idx]}")

        # Perform the best move
        start, end = best_move
        self.move_piece(start, end)
        return True

    def get_fen(self):
        """
        Generate the FEN string for the current board state.
        :return: A FEN string representing the board.
        """
        import chess
        board = chess.Board()
        board.clear()  # Start with an empty board

        # Place pieces on the board according to self.board
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    symbol = piece.__class__.__name__[0].lower()  # Get piece symbol
                    if piece.color == 'white':
                        symbol = symbol.upper()  # White pieces are uppercase
                    square = chess.square(col, 7 - row)  # Translate to 0-indexed square
                    board.set_piece_at(square, chess.Piece.from_symbol(symbol))

        # Set the turn
        board.turn = (self.current_turn == "white")

        # Handle castling rights
        castling_rights = ""
        for row, rook_col in [(7, 0), (7, 7), (0, 0), (0, 7)]:
            rook = self.board[row][rook_col]
            if isinstance(rook, Rook) and not rook.has_moved:
                if rook.color == 'white' and row == 7:
                    castling_rights += "Q" if rook_col == 0 else "K"
                elif rook.color == 'black' and row == 0:
                    castling_rights += "q" if rook_col == 0 else "k"
        board.set_castling_fen(castling_rights if castling_rights else "-")

        # Handle en passant
        if self.last_move:
            start, end = self.last_move
            if isinstance(self.board[end[0]][end[1]], Pawn):
                if abs(start[0] - end[0]) == 2:  # Pawn moved two spaces
                    board.ep_square = chess.square(end[1], 7 - end[0])

        return board.fen()

