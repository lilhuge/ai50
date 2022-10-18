EMPTY = None

board = [["X", "X", "X"],
        [EMPTY, "X", EMPTY],
        [EMPTY, "X", "X"]]


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

print(lines)

for line in lines:

    if line.count("X") == 3:

        print("X")

    elif line.count("O") == 3:

        print("O")

    else:
        continue

print("None")