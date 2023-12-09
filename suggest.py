from search_driver import SearchDriver


def suggest(board, active, value_network, policy_network):
    expansion_factor = 5
    simulation_depth = 20
    driver = SearchDriver(board, active, value_network, policy_network,
                      expansion_factor, simulation_depth)
    moves = driver.mcts_suggest()
    moves.sort(key = lambda x: x[1])
    if active == 1:
        moves.reverse()
    if len(moves) < 5:
        return moves
    return moves[:5]
