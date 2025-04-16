from fastapi import FastAPI, HTTPException
import random
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

#-------------------------------------------
from board import Board
from solver import Solver
from math import inf

prev_board = None
histories = []
board = Board()

def detect_played_col(prev_board : List[List[int]], current_board : List[List[int]]) -> Optional[int]:
    if prev_board is None:
        return None
    
    for col in range(len(current_board[0])):
        for row in range(len(current_board)):
            if prev_board[row][col] != current_board[row][col]:
                return col
#-------------------------------------------


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]

class AIResponse(BaseModel):
    move: int

@app.post("/api/connect4-move")
async def make_move(game_state: GameState) -> AIResponse:
    try:
        last_move = detect_played_col(prev_board, game_state.board)
        if last_move is not None:
            histories.append(last_move)
            board.play(last_move)
            prev_board = game_state.board
        else:
            board.set_board(histories)
        f = open('test.txt', 'w')
        f.write(str(board))
        f.close()
        #-----------------------------------------------------------
        selected_move = 6
        #-----------------------------------------------------------

        return AIResponse(move=selected_move)
    except Exception as e:
        if game_state.valid_moves:
            return AIResponse(move=game_state.valid_moves[0])
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)