from math import inf
from Board import Board
import pygame

pygame.init()

class solver:
    def __init__(self, board: Board):
        self.board = board
        self.maximizer = board.get_current_player()
        self.minimizer = board.get_opponent()
        self.node_count = 0

    def evaluate(self) -> int:
        if self.board.winning_board_state():
            if self.board.get_opponent() == self.maximizer:
                return 100000
            else:
                return -100000

        grid = self.bitboard_to_grid(self.board)
        return self.score_position(grid, self.maximizer)

    def causes_double_threat(self, col: int) -> bool:
        """Check if playing this column creates two immediate winning threats."""
        self.board.play(col)
        threats = 0
        for next_col in self.board.get_available_moves():
            self.board.play(next_col)
            if self.board.winning_board_state():
                threats += 1
            self.board.backtrack()
        self.board.backtrack()
        return threats >= 2

    def apply_strategic_rules(self, is_maximizer) -> int:
        # Rule 1: Win immediately if possible
        for col in range(self.board.w):
            if self.board.can_play(col):
                self.board.play(col)
                if self.board.winning_board_state():
                    self.board.backtrack()
                    print(f"[Strategic] Winning move found at col {col}")
                    return col
                self.board.backtrack()

        # Rule 2: Block opponent's win
        self.board.moves ^= 1  # Switch to opponent
        for col in range(self.board.w):
            if self.board.can_play(col):
                self.board.play(col)
                if self.board.winning_board_state():
                    self.board.backtrack()
                    self.board.moves ^= 1
                    print(f"[Strategic] Blocking opponent's win at col {col}")
                    return col
                self.board.backtrack()
        self.board.moves ^= 1

        # Rule 3: Block opponent's double threats
        self.board.moves ^= 1
        for col in range(self.board.w):
            if self.board.can_play(col) and self.causes_double_threat(col):
                self.board.moves ^= 1
                print(f"[Strategic] Blocking opponent's double threat at col {col}")
                return col
        self.board.moves ^= 1

        return None

    def bitboard_to_grid(self, board: Board):
        grid = [[0 for _ in range(board.w)] for _ in range(board.h)]
        for col in range(board.w):
            for row in range(board.h):
                pos = 1 << ((board.h + 1) * col + row)
                if board.board_state[0] & pos:
                    grid[row][col] = 1
                elif board.board_state[1] & pos:
                    grid[row][col] = 2
        return grid

    def score_position(self, grid, player):
        opponent = 2 if player == 1 else 1
        score = 0

        def evaluate_window(window):
            score = 0
            # Đánh giá cho người chơi hiện tại
            if window.count(player) == 4:
                score += 10000
            elif window.count(player) == 3 and window.count(0) == 1:
                score += 80
            elif window.count(player) == 2 and window.count(0) == 2:
                score += 10

            # Đánh giá cho đối thủ với hình phạt nặng hơn
            if window.count(opponent) == 4:
                score -= 10000
            elif window.count(opponent) == 3 and window.count(0) == 1:
                score -= 200  # Phạt nặng hơn cho nước 3 của đối thủ (trước đây là -120)
            elif window.count(opponent) == 2 and window.count(0) == 2:
                score -= 50   # Phạt nặng hơn khi empty = 2 (trước đây là -20)
            return score

        # Ưu tiên cột giữa
        center_col = len(grid[0]) // 2
        center_count = sum([1 for r in range(len(grid)) if grid[r][center_col] == player])
        score += center_count * 6

        # Duyệt qua các cửa sổ 4 ô trên lưới
        rows, cols = len(grid), len(grid[0])
        # Hàng ngang
        for r in range(rows):
            for c in range(cols - 3):
                window = [grid[r][c + i] for i in range(4)]
                score += evaluate_window(window)
        # Cột dọc
        for r in range(rows - 3):
            for c in range(cols):
                window = [grid[r + i][c] for i in range(4)]
                score += evaluate_window(window)
        # Đường chéo chính (/)
        for r in range(rows - 3):
            for c in range(cols - 3):
                window = [grid[r + i][c + i] for i in range(4)]
                score += evaluate_window(window)
        # Đường chéo phụ (\)
        for r in range(3, rows):
            for c in range(cols - 3):
                window = [grid[r - i][c + i] for i in range(4)]
                score += evaluate_window(window)

        return score

    def solve(self, depth: int, alpha: int, beta: int, is_maximizer) -> tuple:
        self.node_count += 1
        if depth == 0 or self.board.winning_board_state() or self.board.is_full():
            return self.evaluate(), None

        strategic_col = self.apply_strategic_rules(is_maximizer)
        if strategic_col is not None:
            self.board.play(strategic_col)
            score = self.evaluate()
            self.board.backtrack()
            return score, strategic_col

        if is_maximizer:
            eval = -inf
            best_col = None
            for col in self.board.get_available_moves():
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
            for col in self.board.get_available_moves():
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
    board = Board()
    solver_instance = solver(board)
    depth = 5
    alpha = -inf
    beta = inf
    is_maximizer = True

    while True:
        user_input = input("Enter column to play (0-6): ")
        if not user_input.isdigit():
            print("Invalid input. Please enter a number between 0 and 6.")
            continue

        col = int(user_input)
        if col < 0 or col >= board.w:
            print("Invalid column. Please enter a number between 0 and 6.")
            continue

        if board.can_play(col):
            board.play(col)
            print(f"Played column {col}")
        else:
            print(f"Column {col} is not playable.")
            continue

        print('Current board state:')
        print(board)

        if board.winning_board_state():
            print("You win!")
            break

        if board.is_full():
            print("It's a draw!")
            break

        print("AI is thinking...")
        solver_instance.node_count = 0
        _, best_col = solver_instance.solve(depth, alpha, beta, is_maximizer)
        print(f"Node count: {solver_instance.node_count}")
        print("-----------------------------------")

        if best_col is not None:
            board.play(best_col)
            print(f"AI played column {best_col}")

        if board.winning_board_state():
            print("AI wins!")
            print(board)
            break

        if board.is_full():
            print("It's a draw!")
            break

        print('Current board state:')
        print(board)

if __name__ == "__main__":
    test()