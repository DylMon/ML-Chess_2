import tkinter as tk
from gui.chess_gui import ChessGUI

if __name__ == "__main__":
    # Initialize the Tkinter root and ChessGUI
    root = tk.Tk()
    gui = ChessGUI(root)

    # Start the Tkinter event loop
    root.mainloop()
