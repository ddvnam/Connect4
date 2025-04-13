import math
import random
import copy
import time
from Board import Board

class Node:
    def __init__(self, board, move=None, parent=None):
        self.board = board  # Board object
        self.move = move    # Column where move was played to reach this state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = board.get_available_moves()

    def ucb1(self, exploration_param=math.sqrt(2)):
        ''' Calculate UCB1 value for node selection '''
        if self.visits == 0:
            return float('inf')
        parent_visits = self.parent.visits if self.parent else 1
        return self.wins / self.visits + exploration_param * math.sqrt(math.log(parent_visits) / self.visits)

    def select_child(self):
        ''' Select child with highest UCB1 value '''
        return max(self.children, key=lambda c: c.ucb1())

    def add_child(self, move, board):
        ''' Add a child node for the given move '''
        child = Node(board, move, self)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        ''' Update node statistics '''
        self.visits += 1
        self.wins += result

import math
import random
import copy

class MCTS:
    def __init__(self, simulations_per_node=5000):
        self.simulations_per_node = simulations_per_node  # Number of simulations per expansion

    def search(self, board):
        ''' Perform MCTS and return win probabilities for each move '''
        root = Node(copy.deepcopy(board))

        # Try all untried moves at the root
        while root.untried_moves:
            # 1. Selection: Start from root
            node = root
            sim_board = copy.deepcopy(board)

            # If we have untried moves, expand one
            move = random.choice(node.untried_moves)
            sim_board.play(move)
            node = node.add_child(move, copy.deepcopy(sim_board))

            # 2. Simulation: Run 1000 simulations
            for _ in range(self.simulations_per_node):
                sim_board_copy = copy.deepcopy(sim_board)
                result = self.simulate(sim_board_copy)
                
                # 3. Backpropagation
                temp_node = node
                while temp_node:
                    temp_node.update(result)
                    temp_node = temp_node.parent

        # Explore existing children to refine estimates
        for _ in range(len(root.children) * self.simulations_per_node):
            node = root
            sim_board = copy.deepcopy(board)

            # 1. Selection
            while node.untried_moves == [] and node.children != []:
                node = node.select_child()
                sim_board.play(node.move)

            # 2. Simulation
            result = self.simulate(copy.deepcopy(sim_board))

            # 3. Backpropagation
            while node:
                node.update(result)
                node = node.parent

        # Calculate win probabilities for each move
        win_rates = {}
        for child in root.children:
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            win_rates[child.move] = win_rate

        return win_rates

    def simulate(self, board):
        ''' Perform a random simulation and return 1 for win, -1 for loss, 0 for draw '''
        sim_board = copy.deepcopy(board)
        current_player = sim_board.get_current_player()

        while not sim_board.is_full():
            if sim_board.winning_board_state():
                return -1 if sim_board.get_opponent() == current_player else 1
            moves = sim_board.get_available_moves()
            if not moves:
                break
            move = random.choice(moves)
            sim_board.play(move)

        # Check final state
        if sim_board.winning_board_state():
            return -1 if sim_board.get_opponent() == current_player else 1
        return 0  # Draw

if __name__ == "__main__":
    board = Board()
    mcts = MCTS()  # 4 seconds per MCTS move

    while True:
        print("\nCurrent board:")
        print(board)

        if board.is_full():
            print("Game over: It's a draw!")
            break

        current_player = board.get_current_player()
        if current_player == 0:  # Human player (x)
            print("Human player (x), enter column (0-6):")
            while True:
                try:
                    col = int(input())
                    if 0 <= col < board.w and board.can_play(col):
                        board.play(col)
                        break
                    else:
                        print("Invalid move. Choose a column (0-6) that's not full.")
                except ValueError:
                    print("Please enter a valid number (0-6).")
        else:  # MCTS player (o)
            print("MCTS player (o) thinking...")
            win_rates = mcts.search(board)
            if not win_rates:
                print("No moves available for MCTS!")
                break
            # Print win rates for each move
            print("Win probabilities for each move:")
            for move, prob in sorted(win_rates.items()):
                print(f"Column {move}: {prob:.2%}")
            # Choose move with highest win rate
            best_move = max(win_rates, key=win_rates.get)
            print(f"MCTS chooses column {best_move} (win rate: {win_rates[best_move]:.2%})")
            board.play(best_move)

        # Check for a win
        if board.winning_board_state():
            print("\nFinal board:")
            print(board)
            winner = 'x' if current_player == 0 else 'o'
            print(f"Game over: Player {winner} wins!")
            break
