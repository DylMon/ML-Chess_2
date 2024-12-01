import pandas as pd
import chess
import chess.pgn
import numpy as np
import os

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), "../games.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "processed_data")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_moves_to_fen(moves):
    """
    Parse the moves column into FEN (Forsyth-Edwards Notation) board states.
    :param moves: A string of moves in algebraic notation.
    :return: A list of FEN strings representing board states.
    """
    board = chess.Board()
    fens = []
    for move in moves.split():
        try:
            board.push_san(move)
            fens.append(board.fen())
        except ValueError:
            print(f"Skipping invalid move: {move}")
            break
    return fens

def preprocess_data():
    """
    Preprocess the chess dataset and save training data.
    """
    print("Reading dataset...")
    df = pd.read_csv(DATA_PATH)

    # Filter games with sufficient moves
    print("Filtering games with at least 10 turns...")
    df = df[df['turns'] >= 10]

    # Prepare data
    input_data = []
    labels = []

    print("Parsing moves and extracting FEN states...")
    for _, row in df.iterrows():
        fens = parse_moves_to_fen(row['moves'])
        winner = row['winner']

        # Assign labels based on the winner
        if winner == "white":
            label = 1
        elif winner == "black":
            label = -1
        else:  # Draw
            label = 0

        # Add each board state and corresponding label
        for fen in fens:
            input_data.append(fen)
            labels.append(label)

    print(f"Processed {len(input_data)} board states.")

    # Save the processed data
    print("Saving data...")
    np.save(os.path.join(OUTPUT_DIR, "board_states.npy"), input_data)
    np.save(os.path.join(OUTPUT_DIR, "labels.npy"), labels)

    print("Data preprocessing completed. Files saved to:", OUTPUT_DIR)

if __name__ == "__main__":
    preprocess_data()
