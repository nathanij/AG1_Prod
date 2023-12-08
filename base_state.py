class BaseState:
    def __init__(self, board, active, model):
        self.board_ = board
        self.active_ = active
        self.model_ = model
        self.size_ = 9
        