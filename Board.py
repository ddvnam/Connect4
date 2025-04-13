import copy

class Board:
    ''' class to store and manipulate connect 4 game states '''

    def __init__(self, width=7, height=6):
        self.w = width
        self.h = height
        self.board_state = [0, 0]
        self.col_heights = [(height + 1) * i for i in range(width)]
        self.moves = 0
        self.history = []
        self.bit_shifts = self.get_bit_shifts()

    def __repr__(self):
        state = []
        for i in range(self.h):                         # row
            row_str = ''
            for j in range(self.w):                     # col
                pos = 1 << (self.h + 1) * j + i
                if self.board_state[0] & pos == pos:
                    row_str += 'x '
                elif self.board_state[1] & pos == pos:
                    row_str += 'o '
                else:
                    row_str += '. '
            state.append(row_str)
        state.reverse()         
        return '\n'.join(state)

    def get_current_player(self):
        ''' returns current player: 0 or 1 (0 always plays first) '''
        return self.moves & 1

    def get_opponent(self):
        ''' returns opponent to current player: 0 or 1 '''
        return (self.moves + 1) & 1

    def get_available_moves(self):
        available_moves = [col for col in range(self.w) if self.can_play(col)]
        # Sort by: 1) Center priority, 2) Column height (higher = better)
        return sorted(available_moves, key=lambda x: (abs(x - self.w // 2), -self.col_heights[x]))

    def get_mask(self):
        ''' returns bitstring of all occupied positions '''
        return self.board_state[0] | self.board_state[1]

    def can_play(self, col):
        ''' returns true if col (zero indexed) is playable '''
        return not self.get_mask() & 1 << (self.h + 1) * col + (self.h - 1)

    def play(self, col):
        player = self.get_current_player()
        move = 1 << self.col_heights[col]
        self.col_heights[col] += 1
        self.board_state[player] |= move
        self.history.append(col)
        self.moves += 1

    def backtrack(self):
        opp = self.get_opponent()
        col = self.history.pop()
        self.col_heights[col] -= 1
        move = 1 << (self.col_heights[col])
        self.board_state[opp] ^= move
        self.moves -= 1

    def winning_board_state(self):
        ''' returns true if last played column creates winning alignment '''
        opp = self.get_opponent()
        for shift in self.bit_shifts:
            test = self.board_state[opp] & (self.board_state[opp] >> shift)
            if test & (test >> 2 * shift):
                return True
        return False

    def is_full(self):
        return self.moves == self.w * self.h
    
    def get_score(self):
        ''' returns score of complete game (evaluated for winning opponent) '''
        return - (self.w * self.h + 1 - self.moves) // 2

    def get_bit_shifts(self):
        return [
            1,              # | vertical
            self.h,         # \ diagonal
            self.h + 1,     # - horizontal
            self.h + 2      # / diagonal
        ]
    
    


