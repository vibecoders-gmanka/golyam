import pygame
import random
import argparse
import socket
import select
from string import ascii_uppercase

BOARD_SIZE = 5
CELL_SIZE = 60
MARGIN = 20
NUM_SHIPS = 3

COLOR_BG = (30, 30, 30)
COLOR_GRID = (200, 200, 200)
COLOR_SHIP = (50, 150, 50)
COLOR_HIT = (200, 0, 0)
COLOR_MISS = (50, 50, 200)

PORT_DEFAULT = 65432

def random_ships():
    ships = set()
    while len(ships) < NUM_SHIPS:
        ships.add((random.randrange(BOARD_SIZE), random.randrange(BOARD_SIZE)))
    return ships

def draw_board(surface, origin, shots, ships, show_ships=False):
    x0, y0 = origin
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = pygame.Rect(x0 + c * CELL_SIZE, y0 + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, COLOR_GRID, rect, 1)
            fill = None
            if (r, c) in shots:
                fill = COLOR_HIT if shots[(r, c)] else COLOR_MISS
            elif show_ships and (r, c) in ships:
                fill = COLOR_SHIP
            if fill:
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(surface, fill, inner)

# Networking helpers

def recv_line(sock):
    data = b''
    while not data.endswith(b'\n'):
        try:
            chunk = sock.recv(1024)
        except socket.timeout:
            continue
        if not chunk:
            raise ConnectionError('Disconnected')
        data += chunk
    return data.decode().strip()

def send_line(sock, msg):
    sock.sendall((msg + '\n').encode())

class Game:
    def __init__(self, sock, host_turn):
        self.sock = sock
        self.host_turn = host_turn
        self.own_ships = random_ships()
        self.own_shots = {}
        self.opponent_shots = {}
        self.running = True

    def check_game_over(self):
        hits = [p for p in self.own_shots if self.own_shots[p]]
        if len(hits) == NUM_SHIPS:
            return 'WIN'
        opp_hits = [p for p in self.opponent_shots if self.opponent_shots[p]]
        if len(opp_hits) == NUM_SHIPS:
            return 'LOSE'
        return None

    def run(self):
        pygame.init()
        width = CELL_SIZE * BOARD_SIZE * 2 + MARGIN * 3
        height = CELL_SIZE * BOARD_SIZE + MARGIN * 2
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Battleship')
        clock = pygame.time.Clock()

        my_board_origin = (MARGIN, MARGIN)
        opp_board_origin = (MARGIN * 2 + CELL_SIZE * BOARD_SIZE, MARGIN)

        turn = self.host_turn
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            if turn:
                # player's turn - handle click
                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    r = (my - opp_board_origin[1]) // CELL_SIZE
                    c = (mx - opp_board_origin[0]) // CELL_SIZE
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if (r, c) not in self.own_shots:
                            send_line(self.sock, f'SHOT {r} {c}')
                            result = recv_line(self.sock)
                            hit = result == 'HIT'
                            self.own_shots[(r, c)] = hit
                            turn = False
            else:
                # opponent's turn
                send_line(self.sock, 'READY')
                msg = recv_line(self.sock)
                if msg.startswith('SHOT'):
                    _, sr, sc = msg.split()
                    r, c = int(sr), int(sc)
                    hit = (r, c) in self.own_ships
                    self.opponent_shots[(r, c)] = hit
                    send_line(self.sock, 'HIT' if hit else 'MISS')
                    turn = True
            # check for game over
            status = self.check_game_over()
            if status:
                send_line(self.sock, f'END {status}')
                self.running = False
            screen.fill(COLOR_BG)
            draw_board(screen, my_board_origin, self.opponent_shots, self.own_ships, show_ships=True)
            draw_board(screen, opp_board_origin, self.own_shots, self.own_ships)
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(description='Battleship with Pygame and sockets')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--host', action='store_true', help='Host a game')
    group.add_argument('--connect', help='Connect to host at ADDRESS')
    parser.add_argument('--port', type=int, default=PORT_DEFAULT)
    args = parser.parse_args()

    if args.host:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', args.port))
        server.listen(1)
        print('Waiting for opponent...')
        conn, addr = server.accept()
        conn.settimeout(0.1)
        sock = conn
        host_turn = True
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.connect, args.port))
        sock.settimeout(0.1)
        host_turn = False

    try:
        Game(sock, host_turn).run()
    finally:
        sock.close()

if __name__ == '__main__':
    main()
