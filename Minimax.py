import numpy as np

class Minimax:
    def __init__(self, depth, player, board):
        self.depth = depth
        self.player = player
        self.NUM_ROWS, self.NUM_COLS = 6, 7
        self.board = board

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if depth == 0 or self.check_winner(board, self.player) or self.check_winner(board, 3 - self.player):
            return self.evaluate(board), None  
        
        if is_maximizing:
            value, best_col = -np.inf, None
            for col in range(self.NUM_COLS):
                new_board = self.drop_piece(board.copy(), col, self.player)
                if new_board is not None:  
                    new_value, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                    if new_value > value:
                        value, best_col = new_value, col
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break
            return value, best_col
        else:
            value, best_col = np.inf, None
            for col in range(self.NUM_COLS):
                new_board = self.drop_piece(board.copy(), col, 3 - self.player)
                if new_board is not None:  
                    new_value, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                    if new_value < value:
                        value, best_col = new_value, col
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
            return value, best_col

    def drop_piece(self, board, col, player):
        row = self.get_next_open_row(board, col)
        if row is not None:
            board[row, col] = player
            return board
        return None  

    def get_next_open_row(self, board, col):
        for row in range(self.NUM_ROWS - 1, -1, -1):
            if board[row, col] == 0:
                return row
        return None 
    
    def evaluate(self, board):
        return self.evaluate_position(board, self.player) - self.evaluate_position(board, 3 - self.player)

    def evaluate_position(self, board, player):
        score = 0

        # Kiểm tra hàng ngang
        for row in range(self.NUM_ROWS):
            for col in range(self.NUM_COLS - 3):
                score += self.score_window(board[row, col:col + 4], player)

        # Kiểm tra cột dọc
        for col in range(self.NUM_COLS):
            for row in range(self.NUM_ROWS - 3):
                score += self.score_window(board[row:row + 4, col], player)

        # Kiểm tra đường chéo chính
        for row in range(self.NUM_ROWS - 3):
            for col in range(self.NUM_COLS - 3):
                window = [board[row + i, col + i] for i in range(4)]
                score += self.score_window(window, player)

        # Kiểm tra đường chéo phụ
        for row in range(3, self.NUM_ROWS):
            for col in range(self.NUM_COLS - 3):
                window = [board[row - i, col + i] for i in range(4)]
                score += self.score_window(window, player)

        return score

    def score_window(self, window, player):
        opponent = 3 - player
        count_player = sum(1 for x in window if x == player)
        count_opponent = sum(1 for x in window if x == opponent)
        count_empty = sum(1 for x in window if x == 0)

        if count_player == 4:  
            return 100  
        elif count_player == 3 and count_empty == 1:  
            return 10  
        elif count_player == 2 and count_empty == 2:  
            return 5  
        elif count_opponent == 4:  
            return -100  
        elif count_opponent == 3 and count_empty == 1:  
            return -10  
        elif count_opponent == 2 and count_empty == 2:  
            return -5  
        return 0  

    def check_winner(self, board, player):
        for row in range(self.NUM_ROWS):
            for col in range(self.NUM_COLS):
                if board[row, col] == player:
                    if self.check_horizontal(board, row, col, player) or \
                       self.check_vertical(board, row, col, player) or \
                       self.check_diagonal(board, row, col, player):
                        return True
        return False
    
    def check_horizontal(self, board, row, col, player):
        return col + 3 < self.NUM_COLS and all(board[row, col + i] == player for i in range(4))
    
    def check_vertical(self, board, row, col, player):
        return row + 3 < self.NUM_ROWS and all(board[row + i, col] == player for i in range(4))
    
    def check_diagonal(self, board, row, col, player):
        return (row + 3 < self.NUM_ROWS and col + 3 < self.NUM_COLS and all(board[row + i, col + i] == player for i in range(4))) or \
               (row - 3 >= 0 and col + 3 < self.NUM_COLS and all(board[row - i, col + i] == player for i in range(4)))
