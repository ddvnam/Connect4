from math import inf
from Board import Board
import pygame

pygame.init()

class Solver:  # Changed to PascalCase for class naming convention
    def __init__(self, board: Board):
        self.board = board
        self.maximizer = board.get_current_player()
        self.minimizer = board.get_opponent()
        self.node_count = 0
        self.pruning_count = 0

    def evaluate(self) -> int:
        if self.board.winning_board_state():
            return 1000000 if self.board.get_opponent() == self.maximizer else -1000000

        grid = self.bitboard_to_grid(self.board)
        return self.score_position(grid, self.maximizer)

    def causes_double_threat(self, col: int) -> bool:
        """Check if playing this column creates two immediate winning threats."""
        if not self.board.can_play(col):
            return False
            
        self.board.play(col)
        threats = 0
        for next_col in self.board.get_available_moves():
            if self.board.can_play(next_col):
                self.board.play(next_col)
                if self.board.winning_board_state():
                    threats += 1
                self.board.backtrack()
                if threats >= 2:  # Early exit if we already found 2 threats
                    break
        self.board.backtrack()
        return threats >= 2

    def apply_strategic_rules(self, is_maximizer) -> int:
        current_player = self.maximizer if is_maximizer else self.minimizer
        opponent = self.minimizer if is_maximizer else self.maximizer

        # Rule 1: Win immediately if possible
        for col in self.board.get_available_moves():
            if self.board.can_play(col):
                self.board.play(col)
                if self.board.winning_board_state() and self.board.get_current_player() == opponent:  # Check if we won
                    self.board.backtrack()
                    return col
                self.board.backtrack()

        # Rule 2: Block opponent's win
        # Temporarily switch to opponent's perspective
        original_player = self.board.get_current_player()
        self.board.moves ^= 1
        for col in self.board.get_available_moves():
            if self.board.can_play(col):
                self.board.play(col)
                if self.board.winning_board_state():
                    self.board.backtrack()
                    self.board.moves = original_player  # Restore original player
                    return col
                self.board.backtrack()
        self.board.moves = original_player  # Restore original player

        # Rule 3: Block opponent's double threats
        for col in self.board.get_available_moves():
            if self.board.can_play(col) and self.causes_double_threat(col):
                return col

        return None

    def bitboard_to_grid(self, board: Board):
        grid = [[0 for _ in range(board.w)] for _ in range(board.h)]
        for col in range(board.w):
            for row in range(board.h):
                pos = 1 << ((board.h + 1) * col + row)
                if board.board_state[0] & pos:
                    grid[row][col] = 1  # Quân của người chơi 1
                elif board.board_state[1] & pos:
                    grid[row][col] = 2  # Quân của người chơi 2
        return grid[::-1]  # Đảo ngược hàng để hàng 0 là đáy bàn cờ

    def score_position(self, grid, player):
        player += 1
        opponent = 3 - player  # Assuming players are 1 and 2

        score = 0
        def evaluate_window(window):
            player_count = window.count(player)
            opponent_count = window.count(opponent)
            empty_count = window.count(0)

            # Terminal cases (win/loss)
            if player_count == 4:
                return 100000
            if opponent_count == 4:
                return -100000

            window_score = 0

            # Player's opportunities
            if player_count == 3 and empty_count == 1:
                window_score += 100
            elif player_count == 2 and empty_count == 2:
                window_score += 10
            elif player_count == 3 and empty_count == 2:
                window_score += 50

            # Opponent's threats
            if opponent_count == 3 and empty_count == 1:
                window_score -= 500
            elif opponent_count == 2 and empty_count == 2:
                window_score -= 20
            elif opponent_count == 3 and empty_count == 2:
                window_score -= 300

            return window_score

        # Center column priority
        center_col = len(grid[0]) // 2
        center_count = sum(1 for r in range(len(grid)) if grid[r][center_col] == player)
        score += center_count * 3

        # Window evaluation
        rows, cols = len(grid), len(grid[0])
        
        # Horizontal
        for r in range(rows):
            for c in range(cols - 3):
                window = (grid[r][c], grid[r][c+1], grid[r][c+2], grid[r][c+3])
                score += evaluate_window(window)
        
        # Vertical
        for c in range(cols):
            for r in range(rows - 3):
                window = (grid[r][c], grid[r+1][c], grid[r+2][c], grid[r+3][c])
                score += evaluate_window(window)
        
        # Diagonal (positive slope)
        for r in range(rows - 3):
            for c in range(cols - 3):
                window = (grid[r][c], grid[r+1][c+1], grid[r+2][c+2], grid[r+3][c+3])
                score += evaluate_window(window)
        
        # Diagonal (negative slope)
        for r in range(3, rows):
            for c in range(cols - 3):
                window = (grid[r][c], grid[r-1][c+1], grid[r-2][c+2], grid[r-3][c+3])
                score += evaluate_window(window)

        return score

    def solve(self, depth: int, alpha: int, beta: int, is_maximizer: bool) -> tuple:
        # Kiểm tra terminal node trước khi đếm node
        if depth == 0 or self.board.winning_board_state() or self.board.is_full():
            return self.evaluate(), None

        self.node_count += 1  # Chỉ đếm node khi thực sự duyệt

        strategic_col = self.apply_strategic_rules(is_maximizer)
        if strategic_col is not None and self.board.can_play(strategic_col):
            self.board.play(strategic_col)
            score = self.evaluate()
            self.board.backtrack()
            return score, strategic_col

        best_col = None
        eval_score = -inf if is_maximizer else inf

        for col in self.board.get_available_moves():
            if not self.board.can_play(col):
                continue

            self.board.play(col)
            current_score, _ = self.solve(depth - 1, alpha, beta, not is_maximizer)
            self.board.backtrack()

            if is_maximizer:
                if current_score > eval_score:
                    eval_score = current_score
                    best_col = col
                alpha = max(alpha, eval_score)
            else:
                if current_score < eval_score:
                    eval_score = current_score
                    best_col = col
                beta = min(beta, eval_score)

            if beta <= alpha:
                if hasattr(self, 'pruning_count'):
                    self.pruning_count += 1  # Chỉ tăng khi cắt tỉa
                print(f"Pruning at depth {depth} for column {col} with alpha {alpha} and beta {beta} | Node count: {self.node_count}")
            
                break

        return eval_score, best_col
    
def test():
    board = Board()
    solver_instance = Solver(board)  # Changed to match class name
    depth = 8
    alpha = -inf
    beta = inf
    is_maximizer = True

    while True:
        print("AI is thinking...")
        solver_instance.node_count = 0
        start = pygame.time.get_ticks()
        _, best_col = solver_instance.solve(depth, alpha, beta, is_maximizer)
        print(f"Node count: {solver_instance.node_count}")
        print(f'Time taken: {pygame.time.get_ticks() - start} ms')
        print("-----------------------------------")

        if best_col is not None and board.can_play(best_col):
            board.play(best_col)
            print(f"AI played column {best_col}")
        else:
            print("No valid move found!")
            break

        if board.winning_board_state():
            print("AI wins!")
            print(board)
            break

        if board.is_full():
            print("It's a draw!")
            break

        print('Current board state:')
        print(board)

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
                break
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

if __name__ == "__main__":
    test()
