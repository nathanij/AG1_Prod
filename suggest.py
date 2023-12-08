from base_state import BaseState


def suggest(board, active, model):
    state = BaseState(board, active, model)
    moves = state.mcts_suggest()
    moves.sort(key = lambda x: x[1])
    if active == 1:
        moves.reverse()
    if len(moves) < 5:
        return moves
    return moves[:5]
