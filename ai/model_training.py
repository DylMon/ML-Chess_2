import numpy as np
import tensorflow as tf
import chess
import chess.engine
import os

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "processed_data")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "chess_model.h5")

# Load the preprocessed data
board_states = np.load(os.path.join(DATA_DIR, "board_states.npy"))
labels = np.load(os.path.join(DATA_DIR, "labels.npy"))

def fen_to_matrix(fen):
    """
    Convert FEN string into an 8x8x12 matrix representation.
    :param fen: FEN string.
    :return: A 3D NumPy array representing the board state.
    """
    board = chess.Board(fen)
    matrix = np.zeros((8, 8, 12), dtype=int)

    piece_to_channel = {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,  # White pieces
        'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11  # Black pieces
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            matrix[row, col, piece_to_channel[piece.symbol()]] = 1

    return matrix

# Convert FEN strings to matrices
print("Converting FEN strings to matrices...")
X = np.array([fen_to_matrix(fen) for fen in board_states])
y = np.array(labels)

# Normalize labels to -1, 0, 1
y = y.astype(float)

# Define the model
print("Building the neural network model...")
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(8, 8, 12)),
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1, activation='tanh')
])


model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

# Train the model
print("Training the model...")
model.fit(X, y, validation_split=0.1, epochs=10, batch_size=64)

# Save the model
print("Saving the trained model...")
model.save(MODEL_PATH)
print("Model saved to:", MODEL_PATH)
