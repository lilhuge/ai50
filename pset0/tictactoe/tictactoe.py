"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    
    if sum([row.count(None) for row in board]) % 2 != 0:
        player_turn = "X"
        
    else:
        player_turn = "O"
    
    return player_turn    


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    
    for i, row in enumerate(board):
        for j, column in enumerate(board):
            
            if board[i][j] == None:
                actions.add((i, j))
                
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0]
    j = action[1]
    
    if board[i][j] != None:
        raise NameError('Not Possible')
    
    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    lines = []
    
    for row in board:
        
        lines.append(row)
        
    for j, column in enumerate(board[0]):
        
        col = []
    
        for i, row in enumerate(board):
            col.append(board[i][j])
        
        lines.append(col)    
        
    lines.append((board[0][0], board[1][1], board[2][2]))
    lines.append((board[0][2], board[1][1], board[2][0]))
    
    for line in lines:
        
        if line.count("X") == 3:
                
            return "X"
            
        elif line.count("O") == 3:
            
            return "O"
        
        else:
            continue
            
    return None    
    

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
        
    elif sum([row.count(None) for row in board]) == 0:
        return True
    
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
        
    elif winner(board) == "O":
        return -1
    
    else:
        return 0

def max_value(board):
    
    v = -1
    if terminal(board) == True:
        return utility(board)
    
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v    

def min_value(board):
    
    v = 1
    if terminal(board) == True:
        return utility(board)
    
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v   

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board) == True:
        return None
    
    actions = actions(board)
    act_ratings = []
    
    if player(board) == "X":
        
        for action in actions:
            act_ratings.append(max_value(board))
    
        return actions[act_ratings.index(max(act_ratings))]
        
    else:
        
        for action in actions:
            act_ratings.append(min_value(board))
            
        return actions[act_ratings.index(min(act_ratings))]       
            

        
    
        

    
    
