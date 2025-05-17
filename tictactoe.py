# Simple Tic-Tac-Toe game for two players

from typing import List, Optional


def print_board(board: List[str]) -> None:
    """Display the current board state."""
    print()
    for row in range(3):
        print(" | ".join(board[row * 3:(row + 1) * 3]))
        if row < 2:
            print("---------")
    print()


def check_win(board: List[str]) -> Optional[str]:
    """Return the winning symbol if a player has won, otherwise None."""
    lines = [
        board[0:3], board[3:6], board[6:9],  # rows
        board[0:9:3], board[1:9:3], board[2:9:3],  # columns
        [board[0], board[4], board[8]],
        [board[2], board[4], board[6]],
    ]
    for line in lines:
        if line[0] != " " and line.count(line[0]) == 3:
            return line[0]
    return None


def board_full(board: List[str]) -> bool:
    return all(space != " " for space in board)


def main() -> None:
    board = [" "] * 9
    current = "X"

    while True:
        print_board(board)
        move = input(f"Player {current}, choose a position (1-9): ")
        if not move.isdigit() or not 1 <= int(move) <= 9:
            print("Invalid input. Try again.")
            continue
        idx = int(move) - 1
        if board[idx] != " ":
            print("That position is already taken. Try again.")
            continue
        board[idx] = current
        winner = check_win(board)
        if winner:
            print_board(board)
            print(f"Player {winner} wins!")
            break
        if board_full(board):
            print_board(board)
            print("It's a tie!")
            break
        current = "O" if current == "X" else "X"


if __name__ == "__main__":
    main()
