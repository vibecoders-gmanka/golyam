# Naval Battle Game

This repository contains a simple two-player Battleship style game built with
Python and pygame. Players connect over a TCP socket and take turns firing at
one another's fleets.

## Requirements

- Python 3.9+
- `pygame` library (install with `pip install pygame`)

## Usage

One player hosts while the other joins.

```bash
# Host
python3 naval_battle.py --host 9999

# In another terminal or machine, join:
python3 naval_battle.py --join HOST_IP 9999
```

During ship placement you can press `r` to rotate the next ship. Click on your
own board to place ships. After both players finish placement the game begins.
Click on the opponent board to fire. The first player to sink all enemy ships
wins.
