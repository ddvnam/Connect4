class Board:
    ''' class to store and manipulate connect 4 game states '''

    def __init__(self, width=7, height=6):
        self.w = width
        self.h = height
        self.board_state = [0, 0]
        self.col_heights = [(height + 1) * i for i in range(width)]
        self.moves = 0
        self.history = []
        self.node_count = 0
        self.bit_shifts = self.__get_bit_shifts()
        self.base_search_order = self.__get_base_search_order()

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
        state.reverse()         # inverted orientation more readable
        return '\n'.join(state)

    def get_current_player(self):
        ''' returns current player: 0 or 1 (0 always plays first) '''
        return self.moves & 1

    def get_opponent(self):
        ''' returns opponent to current player: 0 or 1 '''
        return (self.moves + 1) & 1

    def get_search_order(self):
        ''' returns column search order containing playable columns only '''
        col_order = filter(self.can_play, self.base_search_order)
        return sorted(col_order, key=self.__col_sort, reverse=True)

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

    def get_score(self):
        ''' returns score of complete game (evaluated for winning opponent) '''
        return (self.w * self.h + 1 - self.moves) // 2

    def __get_bit_shifts(self):
        return [
            1,              # | vertical
            self.h,         # \ diagonal
            self.h + 1,     # - horizontal
            self.h + 2      # / diagonal
        ]

    def __get_base_search_order(self):
        base_search_order = list(range(self.w))
        base_search_order.sort(key=lambda x: abs(self.w // 2 - x))
        return base_search_order

    def __col_sort(self, col):
        player = self.get_current_player()
        move = 1 << self.col_heights[col]
        count = 0
        state = self.board_state[player] | move

        for shift in self.bit_shifts:
            test = state & (state >> shift) & (state >> 2 * shift)
            if test:
                count += bin(test).count('1')

        return count
    
    def is_full(self):
        return self.moves == self.w*self.h
    
    @staticmethod
    def from_list(board_list):
        """
        Convert a list representation of Connect 4 board to a BitBoard object.
        
        Args:
            board_list: A 2D list (height x width) representing the board state,
                    where 0 = empty, 1 = player 0 (x), 2 = player 1 (o)
        
        Returns:
            A new Board object initialized with the given state
        """
        height = len(board_list)
        if height == 0:
            return Board()
        width = len(board_list[0])
        
        bitboard = Board(width, height)
        
        # Clear the initial empty state
        bitboard.board_state = [0, 0]
        bitboard.moves = 0
        bitboard.history = []
        bitboard.col_heights = [(height + 1) * i for i in range(width)]
        
        # We need to process the board from bottom to top (as in physical Connect 4)
        for row in range(height):
            for col in range(width):
                player = board_list[height - 1 - row][col]  # height-1-row converts to bottom-up
                if player == 1:  # Player 0
                    bitboard.board_state[0] |= 1 << (bitboard.col_heights[col])
                    bitboard.col_heights[col] += 1
                    bitboard.moves += 1
                    bitboard.history.append(col)
                elif player == 2:  # Player 1
                    bitboard.board_state[1] |= 1 << (bitboard.col_heights[col])
                    bitboard.col_heights[col] += 1
                    bitboard.moves += 1
                    bitboard.history.append(col)
        
        return bitboard
