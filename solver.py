import math
from Board import Board
import pygame

pygame.init()

class Solver:
    def __init__(self, board: Board):
        self.board = board
        self.maximizer = board.get_current_player()
        self.minimizer = board.get_opponent()
        self.node_count = 0
    
    def evaluate(self) -> int:
        """Evaluate board with win/loss detection"""
        if self.board.is_winning_state(self.maximizer):
            return 10000 + self.board.moves  # Prefer faster wins
        if self.board.is_winning_state(self.minimizer):
            return -10000 - self.board.moves
        return 0  # Neutral score for non-terminal states

    def solve(self, depth: int, alpha: int, beta: int, is_maximizer: bool) -> tuple:
        self.node_count += 1
        
        # Immediate terminal state check
        if self.board.is_winning_state(self.maximizer):
            return 10000 + depth, None
        if self.board.is_winning_state(self.minimizer):
            return -10000 - depth, None
        if depth == 0 or self.board.is_draw():
            return self.evaluate(), None

        # Check for immediate winning/blocking moves
        best_col = None
        available_moves = self.board.get_available_moves()
        
        # 1. Check if we can win immediately
        if is_maximizer:
            for col in available_moves:
                self.board.play(col)
                if self.board.is_winning_state(self.maximizer):
                    self.board.undo()
                    return 10000 + depth, col  # Immediate win
                self.board.undo()
        
        # 2. Check if opponent can win next move (must block)
        for col in available_moves:
            self.board.play(col)
            if self.board.is_winning_state(self.minimizer):
                self.board.undo()
                if not is_maximizer:  # Opponent's winning move
                    return -10000 - depth, col
                else:  # We must block this
                    blocked_score, _ = self.solve(depth-1, alpha, beta, False)
                    self.board.play(col)  # Try the block
                    score_after_block = self.evaluate()
                    self.board.undo()
                    return min(blocked_score, score_after_block), col
            self.board.undo()

        # 3. Regular minimax search if no immediate threats
        if is_maximizer:
            max_eval = -math.inf
            for col in available_moves:
                self.board.play(col)
                current_eval, _ = self.solve(depth-1, alpha, beta, False)
                self.board.undo()
                
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_col = col
                    alpha = max(alpha, max_eval)
                    if beta <= alpha:
                        break
            return max_eval, best_col
        else:
            min_eval = math.inf
            for col in available_moves:
                self.board.play(col)
                current_eval, _ = self.solve(depth-1, alpha, beta, True)
                self.board.undo()
                
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_col = col
                    beta = min(beta, min_eval)
                    if beta <= alpha:
                        break
            return min_eval, best_col



        