EMPTY = None

board = [[EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]]
  
i = 0
j = 1
    
if board[i][j] != None:
    raise NameError('Not Possible')
    
new_board = board
new_board[i][j] = "X"  
  
print(new_board)
      
#print(board)
#print(sum([row.count(None) for row in board]))

#actions = set()
    
#for i, row in enumerate(board):
#    for j, column in enumerate(board):
        
#        if board[i][j] == None:
#            actions.add((i, j))
#print(actions)