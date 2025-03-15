import pygame
import numpy as np
import Minimax

class Connect4:
    NUM_ROWS, NUM_COLS = 6, 7
    SQUARE_SIZE = 100
    RADIUS = SQUARE_SIZE // 2 - 5
    SCREEN_WIDTH, SCREEN_HEIGHT = NUM_COLS * SQUARE_SIZE, NUM_ROWS * SQUARE_SIZE
    FPS = 60
    COLORS = {
        "PLAYER1": (20, 200, 170),
        "PLAYER2": (30, 50, 70),
        "BACKGROUND": (230, 235, 240),
        "EMPTY_SLOT": (255, 255, 255),
    }

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Connect Four Board")
        self.board = np.zeros((self.NUM_ROWS, self.NUM_COLS))
        self.turn = 1
        self.running = True
        self.game_loop()

    def game_loop(self):
        while self.running:  
            self.event_handler()
            self.draw()  
            self.setFPS()
        pygame.quit()
    
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.turn == 1 and event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // self.SQUARE_SIZE
                self.drop_piece(col)
            if self.turn == 2:
                score, col = Minimax.Minimax(4, 2, self.board).minimax(self.board, 5, -np.inf, np.inf, True)
                self.drop_piece(col)
                


    def reset(self):
        self.board = np.zeros((self.NUM_ROWS, self.NUM_COLS))
        self.turn = 1
        self.running = True
        pygame.time.delay(3000)

    def check_winner(self, player):
        for row in range(self.NUM_ROWS):
            for col in range(self.NUM_COLS):
                if self.board[row, col] == player:
                    if self.check_horizontal(row, col, player) or self.check_vertical(row, col, player) or self.check_diagonal(row, col, player):
                        return True
    
    def check_horizontal(self, row, col, player):
        return col + 3 < self.NUM_COLS and all(self.board[row, col + i] == player for i in range(4))
    
    def check_vertical(self, row, col, player):
        return row + 3 < self.NUM_ROWS and all(self.board[row + i, col] == player for i in range(4))
    
    def check_diagonal(self, row, col, player):
        return row + 3 < self.NUM_ROWS and col + 3 < self.NUM_COLS and all(self.board[row + i, col + i] == player for i in range(4)) or \
               row - 3 >= 0 and col + 3 < self.NUM_COLS and all(self.board[row - i, col + i] == player for i in range(4))

    def drop_piece(self, col):
        if self.is_valid_location(col):  
            row = self.get_next_open_row(col)
            if row is not None:  
                self.board[row, col] = self.turn
                self.turn = 3 - self.turn  
        
        if self.check_winner(1):
            self.draw()
            print("Player 1 wins!")
            self.reset()
        elif self.check_winner(2):
            self.draw()
            print("Player 2 wins!")
            self.reset()
        else:
            if all(self.board[0, :]):
                print("It's a tie!")
                self.reset()

    def is_valid_location(self, col):
        return self.board[0, col] == 0  

    def get_next_open_row(self, col):
        for row in range(self.NUM_ROWS - 1, -1, -1):
            if self.board[row, col] == 0:
                return row
        return None  

    def draw(self):
        self.draw_board()
        pygame.display.flip()  

    def draw_board(self):
        self.screen.fill(self.COLORS["BACKGROUND"])
        for row in range(self.NUM_ROWS):
            for col in range(self.NUM_COLS):
                pygame.draw.circle(self.screen, self.COLORS["EMPTY_SLOT"],
                                   (col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                                    row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2),
                                   self.RADIUS)
                if self.board[row, col] == 1:
                    pygame.draw.circle(self.screen, self.COLORS["PLAYER1"],
                                       (col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                                        row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2),
                                       self.RADIUS)
                elif self.board[row, col] == 2:
                    pygame.draw.circle(self.screen, self.COLORS["PLAYER2"],
                                       (col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                                        row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2),
                                       self.RADIUS)

    def setFPS(self):
        self.clock.tick(self.FPS)

if __name__ == "__main__":
    Connect4()
