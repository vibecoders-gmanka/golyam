# Naval combat (Battleship) game using pygame with basic network play via sockets.
# Run as host: python3 naval_battle.py --host <port>
# Run as client: python3 naval_battle.py --join <host_ip> <port>

import pickle
import socket
import sys
import threading
from dataclasses import dataclass
from typing import List, Tuple

import pygame

CELL_SIZE = 40
BOARD_SIZE = 10
SCREEN_WIDTH = CELL_SIZE * BOARD_SIZE * 2 + 50
SCREEN_HEIGHT = CELL_SIZE * BOARD_SIZE + 100

SHIPS = [
    ("Carrier", 5),
    ("Battleship", 4),
    ("Cruiser", 3),
    ("Submarine", 3),
    ("Destroyer", 2),
]


@dataclass
class Ship:
    name: str
    length: int
    positions: List[Tuple[int, int]]
    hits: int = 0

    def is_sunk(self) -> bool:
        return self.hits >= self.length


class Board:
    def __init__(self) -> None:
        self.grid = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.ships: List[Ship] = []

    def place_ship(self, x: int, y: int, length: int, horizontal: bool) -> bool:
        if horizontal:
            if x + length > BOARD_SIZE:
                return False
            for i in range(length):
                if self.grid[y][x + i] != 0:
                    return False
            for i in range(length):
                self.grid[y][x + i] = 1
            self.ships.append(Ship("ship", length, [(x + i, y) for i in range(length)]))
        else:
            if y + length > BOARD_SIZE:
                return False
            for i in range(length):
                if self.grid[y + i][x] != 0:
                    return False
            for i in range(length):
                self.grid[y + i][x] = 1
            self.ships.append(Ship("ship", length, [(x, y + i) for i in range(length)]))
        return True

    def receive_shot(self, x: int, y: int) -> str:
        if self.grid[y][x] == 2 or self.grid[y][x] == 3:
            return "repeat"
        if self.grid[y][x] == 1:
            self.grid[y][x] = 2
            for ship in self.ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    if ship.is_sunk():
                        if self.all_sunk():
                            return "win"
                        return "sunk"
            return "hit"
        else:
            self.grid[y][x] = 3
            return "miss"

    def all_sunk(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)


class NetworkHandler(threading.Thread):
    def __init__(self, sock: socket.socket, game: "Game") -> None:
        super().__init__(daemon=True)
        self.sock = sock
        self.game = game

    def run(self) -> None:
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            message = pickle.loads(data)
            self.game.handle_network(message)


class Game:
    def __init__(self, connection: socket.socket, is_host: bool) -> None:
        self.connection = connection
        self.is_host = is_host
        self.player_board = Board()
        self.enemy_board = Board()
        self.current_ship_index = 0
        self.horizontal = True
        self.placing = True
        self.turn = is_host

    def handle_network(self, message: tuple) -> None:
        command = message[0]
        if command == "shot":
            x, y = message[1], message[2]
            result = self.player_board.receive_shot(x, y)
            self.send(("result", x, y, result))
            if result == "win":
                print("You lost!")
                pygame.quit()
                sys.exit()
            self.turn = True
        elif command == "result":
            x, y, result = message[1], message[2], message[3]
            if result in {"hit", "sunk", "win"}:
                self.enemy_board.grid[y][x] = 2
            else:
                self.enemy_board.grid[y][x] = 3
            if result == "win":
                print("You win!")
                pygame.quit()
                sys.exit()
            self.turn = False
        elif command == "ready":
            self.placing = False

    def send(self, message: tuple) -> None:
        self.connection.sendall(pickle.dumps(message))

    def draw_board(
        self,
        screen: pygame.Surface,
        board: Board,
        offset_x: int,
        offset_y: int,
        reveal: bool,
    ) -> None:
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE,
                    offset_y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                cell = board.grid[y][x]
                if cell == 1 and reveal:
                    pygame.draw.rect(screen, (0, 100, 0), rect)
                elif cell == 2:
                    pygame.draw.circle(
                        screen,
                        (255, 0, 0),
                        rect.center,
                        CELL_SIZE // 2 - 4,
                    )
                elif cell == 3:
                    pygame.draw.circle(
                        screen,
                        (0, 0, 255),
                        rect.center,
                        CELL_SIZE // 2 - 4,
                    )

    def place_ships(self, pos: Tuple[int, int]) -> None:
        if self.current_ship_index >= len(SHIPS):
            return
        x = (pos[0] - 10) // CELL_SIZE
        y = (pos[1] - 10) // CELL_SIZE
        if x < 0 or y < 0 or x >= BOARD_SIZE or y >= BOARD_SIZE:
            return
        length = SHIPS[self.current_ship_index][1]
        if self.player_board.place_ship(x, y, length, self.horizontal):
            self.current_ship_index += 1
            if self.current_ship_index >= len(SHIPS):
                self.placing = False
                self.send(("ready",))

    def handle_click(self, pos: Tuple[int, int]) -> None:
        if self.placing:
            self.place_ships(pos)
            return
        if not self.turn:
            return
        x = (pos[0] - (CELL_SIZE * BOARD_SIZE + 30)) // CELL_SIZE
        y = (pos[1] - 10) // CELL_SIZE
        if x < 0 or y < 0 or x >= BOARD_SIZE or y >= BOARD_SIZE:
            return
        if self.enemy_board.grid[y][x] in {2, 3}:
            return
        self.send(("shot", x, y))
        self.turn = False

    def run(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Naval Battle")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.horizontal = not self.horizontal
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)

            screen.fill((200, 200, 200))
            self.draw_board(screen, self.player_board, 10, 10, True)
            self.draw_board(
                screen,
                self.enemy_board,
                CELL_SIZE * BOARD_SIZE + 30,
                10,
                False,
            )

            if self.placing:
                text = font.render(
                    f"Place {SHIPS[self.current_ship_index][0]} (length {SHIPS[self.current_ship_index][1]})",
                    True,
                    (0, 0, 0),
                )
            else:
                text = font.render(
                    "Your turn" if self.turn else "Waiting...",
                    True,
                    (0, 0, 0),
                )
            screen.blit(text, (10, SCREEN_HEIGHT - 40))
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


def start_host(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("", port))
        server.listen(1)
        print(f"Waiting for connection on port {port}...")
        conn, _addr = server.accept()
        print("Player connected.")
        game = Game(conn, True)
        handler = NetworkHandler(conn, game)
        handler.start()
        game.run()


def start_client(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((host, port))
        print("Connected to host.")
        game = Game(conn, False)
        handler = NetworkHandler(conn, game)
        handler.start()
        game.run()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 naval_battle.py --host <port> | --join <host> <port>")
        sys.exit(1)
    if sys.argv[1] == "--host":
        port = int(sys.argv[2])
        start_host(port)
    elif sys.argv[1] == "--join":
        host = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 9999
        start_client(host, port)
    else:
        print("Invalid arguments")
