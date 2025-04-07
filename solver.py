from math import inf
from Board import Board
from pygame import time

class solver:
    def __init__(self, board: Board):
        self.board = board
        self.maximizer = board.get_current_player()
        self.minimizer = board.get_opponent()
        self.node_count = 0
    
    def evaluate(self) -> int:
        score = 0
        if self.board.winning_board_state():
            if self.board.get_opponent() == self.maximizer:
                score += self.board.get_score()
            else:
                score -= self.board.get_score()

        return score


    def solve(self, depth: int, alpha: int, beta: int, is_maximizer) -> tuple:
        self.node_count += 1
        if depth == 0 or self.board.winning_board_state() or self.board.is_full():
            return self.evaluate(), None
        
        if is_maximizer:
            eval = -inf
            best_col = None
            for col in self.board.get_search_order():
                self.board.play(col)
                score, _ = self.solve(depth - 1, alpha, beta, False)
                self.board.backtrack()

                if score > eval:
                    eval = score
                    best_col = col

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        else:
            eval = inf
            best_col = None
            for col in self.board.get_search_order():
                self.board.play(col)
                score, _ = self.solve(depth - 1, alpha, beta, True)
                self.board.backtrack()

                if score < eval:
                    eval = score
                    best_col = col

                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return eval, best_col

def test():
    b = Board()
    s = solver(b)
    
    while True:
        print("Current board state:")
        print(b)
        if b.get_current_player() == 0:
            col = int(input("Enter column (0-6): "))
            if not b.can_play(col):
                print("Invalid move. Try again.")
                continue
            b.play(col)
        else:
            start = time.get_ticks()
            _, col = s.solve(12, -inf, inf, True)
            print(f'Node count: {s.node_count}')
            end = time.get_ticks()
            print(f'Time taken: {end - start} ms')
            if col is not None:
                b.play(col)
            else:
                print("No valid moves left.")
                break
        if b.winning_board_state():
            print("Player", b.get_opponent(), "wins!")
            break
        if b.get_mask() == 0:
            print("It's a draw!")
            break

if __name__ == "__main__":
    test()

        