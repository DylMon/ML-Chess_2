import tkinter as tk
from PIL import Image, ImageTk  # For resizing and displaying images
from logic.board import Board


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")

        # Create the chessboard
        self.canvas = tk.Canvas(root, width=800, height=800)
        self.canvas.pack()

        # Load piece images
        self.piece_images = {}
        self.load_images()

        # Initialize the game board
        self.board = Board()

        # Variables to track the selected piece
        self.selected_piece = None
        self.selected_pos = None

        # Draw the board and pieces
        self.draw_board()
        self.draw_pieces()

        # Bind mouse events for interaction
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def load_images(self):
        """
        Load and resize images for the chess pieces.
        """
        piece_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        colors = ["white", "black"]
        for color in colors:
            for piece in piece_types:
                image_path = f"images/{color}_{piece}.png"  # Assumes images are in 'images' folder
                image = Image.open(image_path).resize((100, 100))
                self.piece_images[f"{color}_{piece}"] = ImageTk.PhotoImage(image)

    def draw_board(self):
        """
        Draw the 8x8 chessboard with alternating light and dark squares.
        """
        for row in range(8):
            for col in range(8):
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                x1, y1 = col * 100, row * 100
                x2, y2 = x1 + 100, y1 + 100
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw_pieces(self):
        """
        Draw the chess pieces on the board based on the game state.
        """
        self.canvas.delete("piece")  # Clear previous piece images
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece:
                    image_key = f"{piece.color}_{piece.__class__.__name__.lower()}"
                    x, y = col * 100 + 50, row * 100 + 50  # Center of the square
                    self.canvas.create_image(x, y, image=self.piece_images[image_key], tags="piece")

    def on_click(self, event):
        col, row = event.x // 100, event.y // 100
        piece = self.board.board[row][col]

        if piece and piece.color == self.board.current_turn:
            self.selected_piece = piece
            self.selected_pos = (row, col)
            print(f"{self.board.current_turn.capitalize()} selected {piece.__class__.__name__} at {self.selected_pos}")
        else:
            print(f"Invalid selection: It's {self.board.current_turn.capitalize()}'s turn.")

    def on_drag(self, event):
        """
        Drag the selected piece visually.
        """
        if self.selected_piece:
            self.canvas.delete("drag_piece")
            image_key = f"{self.selected_piece.color}_{self.selected_piece.__class__.__name__.lower()}"
            self.canvas.create_image(event.x, event.y, image=self.piece_images[image_key], tags="drag_piece")

    def on_release(self, event):
        """
        Handle dropping the piece on a new square.
        """
        if not self.selected_piece:
            return

        # Determine the destination square
        end_col, end_row = event.x // 100, event.y // 100
        start_row, start_col = self.selected_pos

        # Attempt to move the piece
        if self.board.move_piece((start_row, start_col), (end_row, end_col)):
            print(f"Moved {self.selected_piece.__class__.__name__} to {(end_row, end_col)}")
        else:
            print("Invalid move. Try again.")

        # Clear selection and redraw the board
        self.selected_piece = None
        self.selected_pos = None
        self.draw_board()
        self.draw_pieces()


if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()
