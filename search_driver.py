from typing import List, Tuple
from board_state import BoardState
from search_node import SearchNode
import math


class SearchDriver:
    def __init__(self, board, active, value_network, policy_network,
                 expansion_factor, simulation_depth, exploration_factor):
        self.board_ = board
        self.active_ = active
        self.value_network_ = value_network
        self.policy_network_ = policy_network
        self.expansion_factor_ = expansion_factor
        self.simulation_depth_ = simulation_depth
        self.exploration_factor_ = exploration_factor
        self.size_ = 9
        self.root_ = None

    def mcts_suggest(self):
        root_state = BoardState(self.size_, None, self.board_, self.active_)
        self.root_ = SearchNode(None, root_state, 0)
        cur = self.root_
        level = 0
        while level < self.simulation_depth_:
            level += 1
            while not cur.is_leaf():
                cur.add_visit()
                branches = cur.branches()
                if cur.get_active_player() == 1:  # white so maximize
                    max_value = -float('inf')
                    best_child = None
                    for move in branches:
                        child = cur.child_at(move)
                        q = child.average_value()
                        u = self.exploration_score(cur, child)
                        if q + u > max_value:
                            max_value = q + u
                            best_child = child
                    cur = best_child
                else:  # black so minimize
                    min_value = float('inf')
                    best_child = None
                    for move in branches:
                        child = cur.child_at(move)
                        q = child.average_value()
                        u = -self.exploration_score(cur, child)
                        if q + u < min_value:
                            min_value = q + u
                            best_child = child
                    cur = best_child
                level += 1
            cur.add_visit()
            for strength, move, state in self.explore(cur):
                child = cur.add_child(move, strength, state)
                self.evaluate(child)
            added_score, added_children = cur.reeval_leaf()
            if cur == self.root_:
                continue
            cur = cur.ascend()
            while cur != self.root_ and cur is not None:
                cur.reevaluate(added_score, added_children)
                cur = cur.ascend()
        
        return self.child_scores(self.root_)
    
    def exploration_score(self, parent: SearchNode, child: SearchNode) -> float:
        scalar = self.exploration_factor_ * child.policy_score()
        visit_score = math.sqrt(parent.visits() + parent.num_children()) / (1 + child.visits())
        return scalar * visit_score
    
    def explore(self, cur: SearchNode) -> List[Tuple[float, int, SearchNode]]:
        move_strengths = self.policy_eval(cur)
        i = 0
        candidates = []
        while i < len(move_strengths) and len(candidates) < self.expansion_factor_:
            move = move_strengths[i][1]
            result = cur.state().next_move(move)
            if result is not None:
                candidates.append((move_strengths[i][0], move, result))
            i += 1
        return candidates
    
    def policy_eval(self, state: SearchNode) -> List[Tuple[float, int]]:
        position = state.get_state_array()
        policy = self.policy_network_.predict(position)[0]
        pairings = []
        for move, strength in enumerate(policy):
            if (move // 19 < 9 and move % 19 < 9) or move == 361: # Filter moves early
                pairings.append((strength, self.convert(move, 19, 9)))
        pairings.sort(key = lambda x: (x[0], -x[1]), reverse = True)  # Descending strength, ascending move order
        return pairings
    
    def convert(self, move: int, prev: int, new: int) -> int:
        if move == prev ** 2:
            return new ** 2
        old_row = move // prev
        old_col = move % prev
        return old_row * new + old_col
    
    def evaluate(self, child: SearchNode):
        position = child.get_state_array()
        value = self.value_network_.predict(position)[0][0]
        child.set_value(value)

    def child_scores(self, root):
        moves = []
        for move in root.branches():
            child = root.child_at(move)
            moves.append((move, child.average_value()))
        return moves
