from math import inf
from board import Board

class Solver:  # Changed to PascalCase for class naming conventions
    def __init__(self, board: Board):
        self.board = board
        self.maximizer = board.get_current_player()
        self.minimizer = board.get_opponent()
        self.node_count = 0
        self.pruning_count = 0
    
    def bitboard_to_grid(self, board: Board):
        state = []
        for i in range(self.board.h):                         # row
            row = []
            for j in range(self.board.w):                     # col
                pos = 1 << (self.board.h + 1) * j + i
                if self.board.board_state[0] & pos == pos:
                    row.append(1)
                elif self.board.board_state[1] & pos == pos:
                    row.append(2)
                else:
                    row.append(0)
            state.append(row)
        state = state[::-1]
        return state

    def evaluate(self) -> int:
        if self.board.winning_board_state():
            return 1000000 if self.board.get_opponent() == self.maximizer else -1000000

        grid = self.bitboard_to_grid(self.board)
        return self.score_position(grid, self.maximizer)

    def score_position(self, grid, player):
        ROWS = len(grid)
        COLS = len(grid[0])
        WINDOW_LENGTH = 4
        EMPTY = 0
        score = 0
        player = player + 1
        opponent = 3 - player  # Đối thủ là quân còn lại

        def evaluate_window(window, player, row_pos=None):
            score = 0
            is_near_top = row_pos is not None and row_pos <= 2

            # Ưu tiên quân ta
            if window.count(player) == 4:
                score += 100
            elif window.count(player) == 3 and window.count(EMPTY) == 1:
                if is_near_top:
                    score += 2  # giảm mạnh nếu gần top
                else:
                    score += 15
            elif window.count(player) == 2 and window.count(EMPTY) == 2:
                score += 5

            # Phạt khi đối thủ có thế
            if window.count(opponent) == 4:
                score -= 100
            elif window.count(opponent) == 3 and window.count(EMPTY) == 1:
                score -= 80
            elif window.count(opponent) == 2 and window.count(EMPTY) == 2:
                score -= 10

            return score

        def count_double_threats(grid, player):
            count = 0
            for r in range(ROWS):
                for c in range(COLS - 3):
                    window = [grid[r][c + i] for i in range(4)]
                    if window.count(player) == 3 and window.count(EMPTY) == 1:
                        if r > 2:  # chỉ đếm nếu không gần top
                            count += 1

            for c in range(COLS):
                for r in range(ROWS - 3):
                    window = [grid[r + i][c] for i in range(4)]
                    if window.count(player) == 3 and window.count(EMPTY) == 1:
                        if r > 2:
                            count += 1

            for r in range(ROWS - 3):
                for c in range(COLS - 3):
                    window = [grid[r + i][c + i] for i in range(4)]
                    if window.count(player) == 3 and window.count(EMPTY) == 1:
                        if r > 2:
                            count += 1

            for r in range(3, ROWS):
                for c in range(COLS - 3):
                    window = [grid[r - i][c + i] for i in range(4)]
                    if window.count(player) == 3 and window.count(EMPTY) == 1:
                        if r > 2:
                            count += 1
            return count

        # Ưu tiên kiểm soát trung tâm
        center_preference = [3, 2, 4, 1, 5]
        for idx, col in enumerate(center_preference):
            center_array = [grid[r][col] for r in range(ROWS)]
            center_count = center_array.count(player)
            score += center_count * (5 - idx)

        # Duyệt hàng ngang
        for r in range(ROWS):
            row_array = grid[r]
            for c in range(COLS - 3):
                window = row_array[c:c + WINDOW_LENGTH]
                score += evaluate_window(window, player, row_pos=r)

        # Duyệt cột dọc
        for c in range(COLS):
            col_array = [grid[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r + WINDOW_LENGTH]
                score += evaluate_window(window, player, row_pos=r)

        # Duyệt chéo /
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [grid[r + i][c + i] for i in range(WINDOW_LENGTH)]
                score += evaluate_window(window, player, row_pos=r)

        # Duyệt chéo \
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                window = [grid[r - i][c + i] for i in range(WINDOW_LENGTH)]
                score += evaluate_window(window, player, row_pos=r)

        # Thêm điểm nếu có double threats an toàn
        threats = count_double_threats(grid, player)
        if threats >= 2:
            score += 50

        return score


    def solve(self, depth: int, alpha: int, beta: int, is_maximizer: bool) -> tuple:
        # Kiểm tra terminal node trước khi đếm node
        if depth == 0 or self.board.winning_board_state() or self.board.is_full():
            return self.evaluate(), None
        self.node_count += 1  # Chỉ đếm node khi thực sự duyệt

        best_col = None
        eval_score = -inf if is_maximizer else inf

        for col in self.board.get_search_order():
            if not self.board.can_play(col):
                continue

            self.board.play(col)
        
            current_score = None

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
                break

        return eval_score, best_col
