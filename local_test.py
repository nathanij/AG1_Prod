import keras
from suggest import suggest

network_dir = "<path>"
value_network_path = os.path.join(network_dir, "loss_final")
policy_network_path = os.path.join(network_dir, "policy_loss_final")
value_network = keras.models.load_model(value_network_path)
policy_network = keras.models.load_model(policy_network_path)

board = [([0.5] * 9) for _ in range(9)]
moves = suggest(board, 0, value_network, policy_network)
print(moves)
