import random
from string import ascii_uppercase

BOARD_SIZE = 5
NUM_SHIPS = 3
MAX_TURNS = 10

def random_ships():
    ships = set()
    while len(ships) < NUM_SHIPS:
        row = random.randint(0, BOARD_SIZE - 1)
        col = random.randint(0, BOARD_SIZE - 1)
        ships.add((row, col))
    return ships

def print_board(shots):
    header = '  ' + ' '.join(str(i+1) for i in range(BOARD_SIZE))
    print(header)
    for r in range(BOARD_SIZE):
        row_label = ascii_uppercase[r]
        row_cells = []
        for c in range(BOARD_SIZE):
            cell = '~'
            if (r, c) in shots:
                cell = 'X' if shots[(r, c)] else 'O'
            row_cells.append(cell)
        print(f"{row_label} " + ' '.join(row_cells))

def parse_input(move):
    if len(move) < 2:
        return None
    row_char = move[0].upper()
    if row_char not in ascii_uppercase[:BOARD_SIZE]:
        return None
    try:
        col = int(move[1:]) - 1
    except ValueError:
        return None
    row = ascii_uppercase.index(row_char)
    if 0 <= col < BOARD_SIZE:
        return row, col
    return None

def play():
    ships = random_ships()
    shots = {}
    turns = 0
    print("Добро пожаловать в игру 'Морской бой'!")
    print(f"На поле {BOARD_SIZE}x{BOARD_SIZE} спрятано {NUM_SHIPS} корабля.")
    while turns < MAX_TURNS and len([s for s in shots if shots[s]]) < NUM_SHIPS:
        print_board(shots)
        move = input('Введите координаты (например A1): ').strip()
        pos = parse_input(move)
        if pos is None:
            print('Неверный ввод. Попробуйте снова.')
            continue
        if pos in shots:
            print('Вы уже стреляли в эту клетку.')
            continue
        hit = pos in ships
        shots[pos] = hit
        if hit:
            print('Попадание!')
        else:
            print('Мимо.')
        turns += 1
    print_board(shots)
    hits = len([s for s in shots if shots[s]])
    if hits == NUM_SHIPS:
        print('Поздравляем! Вы победили!')
    else:
        print('К сожалению, вы проиграли.')
        print('Корабли находились в следующих клетках:')
        for r, c in ships:
            print(f"{ascii_uppercase[r]}{c+1}", end=' ')
        print()

if __name__ == '__main__':
    play()
