from math import inf
from board import Board
import time

class Solver:  # Changed to PascalCase for class naming conventions
    def __init__(self, board: Board):
        self.board = board
        self.maximizer = board.get_current_player()
        self.minimizer = board.get_opponent()
        self.node_count = 0
        self.pruning_count = 0


    def evaluate(self) -> int:
        if self.board.winning_board_state():
            return 1000000 if self.board.get_opponent() == self.maximizer else -1000000

        return self.score_position(self.board)

    def score_position(self, board: Board):
        player_bb = board.board_state[self.maximizer]
        opponent_bb = board.board_state[self.minimizer]
        score = 0

        # Center column preference
        center_column = 0b0001000 << (self.board.w // 2)  # Example for width=7
        score += 3 * bin(player_bb & center_column).count('1')
        score -= 3 * bin(opponent_bb & center_column).count('1')

        for shift in self.board.bit_shifts:
            # 4 in a row (already handled by winning_board_state)
            
            # 3 in a row with open ends
            player_3 = (player_bb & (player_bb >> shift) & (player_bb >> 2*shift))
            opponent_3 = (opponent_bb & (opponent_bb >> shift) & (opponent_bb >> 2*shift))
            
            # Check if the 3 can be extended to 4 (open ends)
            open_ends_mask = ~board.get_mask()
            player_open_3 = bin((player_3 << (3*shift)) & open_ends_mask).count('1') + \
                        bin((player_3 >> shift) & open_ends_mask).count('1')
            score += 100 * player_open_3
            
            opponent_open_3 = bin((opponent_3 << (3*shift)) & open_ends_mask).count('1') + \
                            bin((opponent_3 >> shift) & open_ends_mask).count('1')
            score -= 80 * opponent_open_3

            # 2 in a row with open ends
            player_2 = (player_bb & (player_bb >> shift))
            opponent_2 = (opponent_bb & (opponent_bb >> shift))
            
            player_open_2 = bin((player_2 << (2*shift)) & open_ends_mask).count('1') + \
                        bin((player_2 >> shift) & open_ends_mask).count('1')
            score += 5 * player_open_2
            
            opponent_open_2 = bin((opponent_2 << (2*shift)) & open_ends_mask).count('1') + \
                            bin((opponent_2 >> shift) & open_ends_mask).count('1')
            score -= 10 * opponent_open_2

        return score
    def solve(self, depth: int, alpha: int, beta: int, is_maximizer: bool) -> tuple:
        # Kiểm tra terminal node trước khi đếm node
        if depth == 0 or self.board.winning_board_state() or self.board.is_full():
            return self.evaluate(), None
        self.node_count += 1  # Chỉ đếm node khi thực sự duyệt

        # check instant win or loss
        for col in range(self.board.w):
            if self.board.can_play(col):
                self.board.play(col)
                if self.board.winning_board_state():
                    self.board.backtrack()
                    return (1000000, col) if is_maximizer else (-1000000, col)
                self.board.backtrack()

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
    
# def test():
#     board = Board()
#     solver_instance = Solver(board)  # Changed to match class name
#     depth = 10
#     alpha = -inf
#     beta = inf
#     is_maximizer = True

#     while True:
#         print("AI is thinking...")
#         solver_instance.node_count = 0
#         start = time.time()
#         _, best_col = solver_instance.solve(depth, alpha, beta, is_maximizer)
#         print(f"Node count: {solver_instance.node_count}")
#         end_time = time.time()
#         print(f'Time taken: {end_time - start} ms')
#         print("-----------------------------------")

#         if best_col is not None and board.can_play(best_col):
#             board.play(best_col)
#             print(f"AI played column {best_col}")
#         else:
#             print("No valid move found!")
#             break

#         if board.winning_board_state():
#             print("AI wins!")
#             print(board)
#             break

#         if board.is_full():
#             print("It's a draw!")
#             break

#         print('Current board state:')
#         print(board)

#         while True:
#              # Get user input and ensure it's a string
#             user_input = int(input("Enter column (0-6): "))
#             col = int(user_input)
#             if col < 0 or col >= board.w:
#                 print("Invalid column. Please enter a number between 0 and 6.")
#                 continue

#             if board.can_play(col):
#                 board.play(col)
#                 print(f"Played column {col}")
#                 break
#             else:
#                 print(f"Column {col} is not playable.")
#                 continue

#         print('Current board state:')
#         print(board)

#         if board.winning_board_state():
#             print("You win!")
#             break

#         if board.is_full():
#             print("It's a draw!")
#             break

# if __name__ == "__main__":
#     test()