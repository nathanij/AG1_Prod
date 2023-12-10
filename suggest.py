from search_driver import SearchDriver
import math


def suggest(board, active, value_network, policy_network):
    expansion_factor = 6
    simulation_depth = 25
    exploration_factor = math.sqrt(2) / 8 
    driver = SearchDriver(board, active, value_network, policy_network,
                      expansion_factor, simulation_depth, exploration_factor)
    moves = driver.mcts_suggest()
    moves.sort(key = lambda x: x[1])
    if active == 1:
        moves.reverse()
    if len(moves) < 5:
        return moves
    return moves[:5]
