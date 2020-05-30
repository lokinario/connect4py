import numpy as np 
import pygame
import sys
import math 
import random
from itertools import groupby, islice

ROW_COUNT = 6
COLUMN_COUNT = 7

HUMAN = 1
AI = 2

game_over = 0
# define what the board is
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board 

def drop_piece(board: np.ndarray, row: int, col: int, piece: int)-> np.ndarray:
    board[row][col] = piece
    return board 

def freeRow(board: np.ndarray, col:int)-> int:
    for i in range(COLUMN_COUNT):
        if board[i][col] == 0:
            return i

def isLegal(board: np.ndarray, col):
    return board[ROW_COUNT -1][col] == 0

def print_board(board: np.ndarray):
    print(np.flip(board,0))

# ai functions

# returns list of columns to drop piece
def possibleMoves(board: np.ndarray, piece: int) -> list:
    moves = list()
    for i in range(COLUMN_COUNT):
        if isLegal(board, i):
            # copy = board.copy()
            # moves.append(drop_piece(copy))
            moves.append(i)
    return moves

# winnging checks 
# returns 0 if no win, 1 if p1 wins, 2 if p2 wins
def winning_move(board, player):
    return winCheck(board) == player
# https://stackoverflow.com/questions/26408462/find-if-element-appears-n-times-in-a-row-in-python-list
def rowWinCheck(board: np.ndarray)->int:
    for row in board:
        if any(sum(1 for _ in islice(g, 4)) == 4 for k, g in groupby(row) if k==1):
            return 1
        elif any(sum(1 for _ in islice(g, 4)) == 4 for k, g in groupby(row) if k==2):
            return 2
    return 0
        # check for 4 in a row 1 or 2 

def colWinCheck(board: np.ndarray)->int:
    transposedBoard = np.transpose(board)
    return rowWinCheck(transposedBoard)

# https://stackoverflow.com/questions/6313308/get-all-the-diagonals-in-a-matrix-list-of-lists-in-python
def diagonalWinCheck(board: np.ndarray)->int:
    diags = [board[::-1,:].diagonal(i) for i in range(-board.shape[0]+1,board.shape[1])]
    diags.extend(board.diagonal(i) for i in range(board.shape[1]-1,-board.shape[0],-1))
    for i in diags:
        if any(sum(1 for _ in islice(g, 4)) == 4 for k, g in groupby(i) if k==1):
            return 1
        elif any(sum(1 for _ in islice(g, 4)) == 4 for k, g in groupby(i) if k==2):
            return 2
    return 0

def winCheck(board: np.ndarray)->int:
    return rowWinCheck(board) + colWinCheck(board) + diagonalWinCheck(board)

# alpha beta pruning algo aka minmaxfunction

def is_terminal_node(board):
    return winCheck(board) > 0 or len(possibleMoves(board,AI)) == 0

# score of board
def windowScore(window, player):
    score = 0
    opponent = HUMAN
    if player == HUMAN:
        opponent = AI 
    
    if window.count(player) == 4: 
        score += 100
    elif window.count(player) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(0) == 2:
        score += 2 
    if window.count(opponent) == 3 and window.count(0) == 1:
        score -= 4

    return score

def heuristic(board, player_piece):
    score = 0
    for row in board:
        score += windowScore(row)
    return score


def abprune(board: np.ndarray, depth: int, alpha: int, beta: int, maximizingPlayer: int) -> (int,int):
    valid_moves = possibleMoves(board,maximizingPlayer)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board,AI):
                return (None,  10000000000000)
            elif winning_move(board,HUMAN):
                return (None, -10000000000000)
            else: 
                return (None, 0)
        else:
            return (None, heuristic(board, AI))
    if maximizingPlayer == 1:
        col = -1
        val = -math.inf
        for i in possibleMoves(board, maximizingPlayer):
            copy = board.copy()
            r = freeRow(board,i)
            drop_piece(copy,r,i,maximizingPlayer)
            newVal = abprune(copy,depth - 1, alpha, beta, 2)[1]
            if newVal > val:
                val = newVal 
                col = i
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return col, val 
    else: 
        col = -1
        val = math.inf 
        for i in possibleMoves(board, maximizingPlayer):
            copy = board.copy()
            r = freeRow(board,i)
            drop_piece(copy,r,i,maximizingPlayer)
            newVal = abprune(copy,depth - 1, alpha, beta, 1)[1]
            if newVal > val:
                val = newVal 
                col = i
            beta = min(beta, val)
            if alpha >= beta: 
                break 
        return col, val 




# game loop
'''
__________      ___.             __                
\______   \ ____\_ |__   _______/  |______ _______ 
 |       _//  _ \| __ \ /  ___/\   __\__  \\_  __ \
 |    |   (  <_> ) \_\ \\___ \  |  |  / __ \|  | \/
 |____|_  /\____/|___  /____  > |__| (____  /__|   
        \/           \/     \/            \/       
'''

while 1:
    input("Welcome to my makeshift cli connect 4\nHit enter to start!")
    game_over = 0
    board = create_board()
    turn = 0 
    winner = -1
    print_board(board)
    while not game_over:
        if turn == 0:
            print("ctrl + c to quit\n")
            while 1:
                move = int(input("input 0-6 to choose what column to drop your piece in: "))
                if(move >= 0 and move <7 and isLegal(board,move)):
                    drop_piece(board,freeRow(board,move),move,HUMAN)
                    check = winCheck(board)
                    if(check > 0):
                        winner = HUMAN
                        game_over = True
                    break 
                print("illegal move\n")
        elif not game_over:
            # random for now
            # while 1:
            #     move = random.randint(0,6)
            #     if(move >= 0 and move <7 and isLegal(board,move)):
            #         r = freeRow(board,move)
            #         drop_piece(board,freeRow(board,move),move,AI)
            #         check = winCheck(board)
            #         if(check > 0):
            #             winner = AI
            #             game_over = True
            #         print("AI chooses {},{}\n".format(r,move))
            #         break 
            
            col, score = abprune(board, 5, -math.inf, math.inf,1)
            if isLegal(board, col):
                row = freeRow(board, col)
                drop_piece(board, row, col, AI)
                if winCheck(board):
                    print("AI wins\n")
                    game_over = True

        print_board(board)
        turn += 1
        turn = turn % 2
        if game_over: 
            print("damn its over and player {} wins".format(winner))