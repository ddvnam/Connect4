# Connect-4 AI Implementation

## Overview
This repository contains the implementation of an Artificial Intelligence (AI) algorithm designed to play the Connect-4 game. The project was developed as part of the Artificial Intelligence course (INT3401E 6) at the University of Technology, Vietnam National University, Hanoi. The AI leverages the **Minimax algorithm** with **Alpha-Beta pruning** and **Bitboard representation** to make optimal moves efficiently.

**Team Members:**
- Đàm Văn Nam
- Nguyễn Tiến Phúc
- Phạm Quang Minh
  
## About Connect-4
Connect-4 is a two-player strategy game played on a 6x7 grid. Players take turns dropping colored discs (red or yellow) into one of the seven columns, with the disc falling to the lowest empty slot in that column. The objective is to form a line of four discs of the same color horizontally, vertically, or diagonally. The game ends in a win when a player achieves this or a draw if the board is filled without a winner.

## Project Goals
The goal of this project is to design and implement an AI capable of:
- Understanding the rules of Connect-4.
- Analyzing the game board's state.
- Predicting opponent moves.
- Making strategic decisions to maximize the chance of winning or forcing a draw.

## Implementation Details
### 1. Game State Representation
- **Board Representation**: The game board is modeled as a 6x7 matrix, where:
  - `0`: Empty cell
  - `1`: Player 1's disc (Red)
  - `2`: Player 2's disc (Yellow)
    
  ![image](https://github.com/user-attachments/assets/e05e77a5-701b-412f-b4d0-5044e6752699)
  ###### Figure1: Visual Representation of the Gridboard Game State

### 2. Minimax Algorithm
The core decision-making algorithm is **Minimax**, which assumes both players play optimally:
- The AI (Maximizer) aims to maximize its score.
- The opponent (Minimizer) aims to minimize the AI's score.
- The algorithm explores the game tree recursively up to a predefined depth and evaluates leaf nodes using an evaluation function.

![image](https://github.com/user-attachments/assets/adfaa9b9-484e-48c8-bb64-fa882b1699b3)
  ###### Figure 2: Representation of the Minimax Game Tree Leading to a Win State
  
### 3. Alpha-Beta Pruning
To optimize Minimax, **Alpha-Beta pruning** is applied:
- Maintains `alpha` (best score for Max) and `beta` (best score for Min).
- Prunes branches that cannot affect the final decision, significantly reducing computation time.
- Move ordering prioritizes central columns (`[3, 2, 4, 1, 5, 0, 6]`) to improve pruning efficiency.

### 4. Evaluation Function
The evaluation function assesses non-terminal board states based on:
- **Central Column Preference**: +3 points per disc in the central column for the AI, -3 for the opponent.
- **Three-in-a-Row (Unblocked)**: +100 points for the AI, -80 for the opponent.
- **Two-in-a-Row (Expandable)**: +5 points for the AI, -10 for the opponent.
- **Win/Loss Check**: Immediate win/loss detection.

### 5. Performance Optimization
- **Move Ordering**: Prioritizing central columns enhances Alpha-Beta pruning efficiency.
- **Bitboard Operations**: Uses bitwise operations for fast board state manipulation and evaluation, leveraging hardware-level speed.
  - The board is also represented using two 64-bit integers to enhance performance.

![image](https://github.com/user-attachments/assets/c0582b0f-8b71-4f42-8b68-4b303c2ce862)

  ###### Figure 3: Representation of the bitboard

  - When we encode the gridboard as a 64-bit number, each player is represented by a separate number. Each number indicates that player's board state, where a 1 means the player occupies the bit position, and a 0 means the player hasn't played in that position. To obtain the overall board state showing all occupied positions, we apply a bitwise OR operation to the two players' board states.

    ![image](https://github.com/user-attachments/assets/162311cf-cfd0-437f-80f9-e9bc4d8ada2b)

 ###### Figure 4: Encoding of Two Players' Bitboard States
 
## Prerequisites
- Python 3.8 or higher
- Required libraries: `numpy` (for bitboard operations, if applicable)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ddvnam/Connect4.git
   cd Connect4
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python solver.py
   ```

## Usage
- Run `solver.py` to start the game and play in the terminal.
- The AI uses the Minimax algorithm with Alpha-Beta pruning to select moves.
- Adjust the search depth in `main` of solver.py to balance performance and AI strength.
