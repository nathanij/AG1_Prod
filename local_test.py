import keras
import os
from suggest import suggest

network_dir = "/Users/nathanieljames/Desktop/weights"
value_network_path = os.path.join(network_dir, "lossfinal")
policy_network_path = os.path.join(network_dir, "policy_loss3")
value_network = keras.models.load_model(value_network_path)
policy_network = keras.models.load_model(policy_network_path)

board = [([0.5] * 9) for _ in range(9)]
print(suggest(board, 0, value_network, policy_network))
input()

board[0][1] = 0
board[1][0] = 0
board[1][1] = 1
board[1][2] = 0
print(suggest(board, 1, value_network, policy_network))
input()

board[8][8] = 1
board[7][7] = 1
print(suggest(board, 0, value_network, policy_network))
