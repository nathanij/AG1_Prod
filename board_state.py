from copy import deepcopy
import random
import numpy as np
from typing import List, Optional, Set, Tuple, Type

class BoardState:
    # TODO: change constructor
    def __init__(self, size = 19, prev = None, board = None, active = None):
        self.size_ = size

        if prev is not None:
            self.board_ = deepcopy(prev.board_)
            self.parent_ = prev
            self.active_ = prev.active_ 
            self.pass_count_ = prev.pass_count_
            self.score_ = deepcopy(prev.score_)

        elif board is not None:
            self.board_ = deepcopy(board)
            self.parent_ = None
            self.active_ = active
            self.pass_count_ = 0
            self.score_ = [0,0]
            
        else:
            row, col = random.randint(0, self.size_ - 1), random.randint(0, self.size_ - 1)
            # TODO: randomize multiple moves after testing (first 4 moves)
            self.board_ = [[0.5] * size for _ in range(size)] # 0 for black, 1 for white
            self.board_[row][col] = 0  # randomized first move
            self.active_ = 1 # white moves post-randomization
            self.pass_count_ = 0
            self.score_ = [0,0]
            self.parent_ = None

    def finished(self) -> bool:
        return self.pass_count_ == 2
    
    def get_state_array(self): # KEEP
        board = deepcopy(self.board_)
        if self.size_ != 19:
            for row in board:
                row += ([0.5] * (19 - self.size_))
            for _ in range(19 - self.size_):
                board.append([0.5] * 19)
        arr = np.asarray(board).astype('float32')
        return arr.reshape(-1,19,19,1)
    
    def get_active_player(self) -> bool:
        return self.active_
    
    def opp(self, color: int) -> int:
        opp = 1 if color == 0 else 0
        return opp
    
    def bfs_(self, row, col, visited, prevs, match_color) -> bool:
        opp_color = self.opp(match_color)
        if row < 0 or col < 0 or row >= self.size_ or col >= self.size_:
            return False
        coord = (row, col)
        if coord in prevs or coord in visited:
            return False
        if self.board_[row][col] == 0.5:
            return True # unrestricted edge
        if self.board_[row][col] == opp_color:
            return False # restricted edge
        
        # implicitly board[row][col] = match color
        if row == 0 or col == 0 or row == self.size_ - 1 or col == self.size_ - 1:
            return True
        prevs.add(coord)

        adj = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        retval = False
        for y,x in adj:
            retval = retval or self.bfs_(y, x, visited, prevs, match_color)
        return retval

    def validate_move_(self, row, col) -> bool:
        # check if space is already occupied
        if self.board_[row][col] != 0.5:
            return False
        
        # set up for bfs
        visited = set()
        captured = []
        move_color = self.active_
        opp_color = self.opp(self.active_)
        self.board_[row][col] = self.active_

        # bfs through adjacent points
        foci = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        for y, x in foci:
            prevs = set()
            if not self.bfs_(y, x, visited, prevs, opp_color):
                for point in prevs:
                    captured.append(point)
            visited.union(prevs)

        # if no captures check if placement has liberties
        if len(captured) == 0:
            if not self.bfs_(row, col, set(), set(), move_color):
                self.board_[row][col] = 0.5
                return False

        # make captures
        for y, x in captured:
            self.board_[y][x] = 0.5

        # check for repeated board state
        cur = self.parent_
        while cur is not None:
            if self.board_ == cur.board_:
                for y, x in captured:
                    self.board_[y][x] = opp_color
                self.board_[row][col] = 0.5
                return False
            cur = cur.parent_
        self.score_[self.active_] += len(captured)
        return True
    
    def next_move(self, move: int) -> Optional[Type['BoardState']]: # KEEP
        res = BoardState(self.size_, self)
        flag = res.make_move(move)
        if flag:
            return res
        return None

    def make_move(self, move: int) -> bool:
        if move == self.size_ ** 2:
            self.pass_count_ += 1
            self.active_ = self.opp(self.active_)
            return True
        row = move // self.size_
        col = move % self.size_
        if not self.validate_move_(row, col):
            return False
        self.pass_count_ = 0
        self.active_ = self.opp(self.active_)
        return True
    
    # returns -1 if open is at liberty or un-surrounded, 0 if black, 1 if white
    def winner_bfs(self, row: int, col: int, visited: Set[Tuple[int, int]]) -> int:
        if self.board_[row][col] == 0:
            return (0, 0)
        if self.board_[row][col] == 1:
            return (1, 0)
        if (row, col) in visited:
            return (2, 0)
        visited.add((row, col))
        if row == 0 or col == 0 or row == self.size_ - 1 or col == self.size_ - 1:
            return (-1, 0)

        res, mag = 2, 1
        adj = [(row - 1, col), (row, col - 1), (row + 1, col), (row, col + 1)]
        for y, x in adj:
            tres, tmag = self.winner_bfs(y, x, visited)
            if tres == -1:
                return (-1, 0)
            elif res == 2:
                res = tres
            elif res != tres:
                return (-1, 0)
            mag += tmag
        return (res, mag)

    def get_winner(self):
        print(f'Pre bfs score: {self.score_}')
        score = self.score_
        visited = set()
        for row in range(self.size_):
            for col in range(self.size_):
                if self.board_[row][col] == 0.5:
                    res, mag = self.winner_bfs(row, col, visited)
                    if res == 0 or res == 1:
                        print(row, col)
                        score[res] += mag
        print(f'Post bfs score: {score}')
        if score[0] > score[1]:
            return 0
        if score[0] == score[1]:
            return 0.5
        return 1
