#!/usr/bin/env python3

from __future__ import annotations

import json
import sys

from enum import Enum
from typing import Callable, Optional


class Dir(int, Enum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7

    def next(self) -> Dir:
        return Dir((self + 1) % len(Dir))

    def invert(self) -> Dir:
        return Dir((self + len(Dir)//2) % len(Dir))


debug: bool = False


class Player:

    def __init__(self, idx: int, x: int, y: int, players: list[Player]) -> None:
        self.idx = idx
        self.x = x
        self.y = y
        self.n: list[list[Player]] = [[] for _ in range(len(Dir))]  # neighbours
        self.out = False    
        self.players = players # for debug

    def __repr__(self) -> str:
        return f"Player(x={self.x}, y={self.y})"

    @staticmethod
    def _insert_neighbour(where: list[Player], what: Player, cmp: Callable[[Player, Player], bool]) -> None:
        i = 0
        while i < len(where) and cmp(what, where[i]):
            i += 1
        where.insert(i, what)

    def add_neighbour(self, other: Player) -> None:
        assert self is not other
        if self.x == other.x:
            if self.y > other.y:
                self._insert_neighbour(
                    self.n[Dir.N],
                    other,
                    lambda this, that: this.y < that.y
                )
            else:
                self._insert_neighbour(
                    self.n[Dir.S],
                    other,
                    lambda this, that: this.y > that.y
                )
        elif self.y == other.y:
            if self.x < other.x:
                self._insert_neighbour(
                    self.n[Dir.E],
                    other,
                    lambda this, that: this.x > that.x
                )
            else:
                self._insert_neighbour(
                    self.n[Dir.W],
                    other,
                    lambda this, that: this.x < that.x
                )
        elif self.x > other.x and self.y < other.y and self.x - other.x == other.y - self.y:
            self._insert_neighbour(
                self.n[Dir.SW],
                other,
                lambda this, that: this.x < that.x
            )
        elif self.x > other.x and self.y > other.y and self.x - other.x == self.y - other.y:
            self._insert_neighbour(
                self.n[Dir.NW],
                other,
                lambda this, that: this.x < that.x
            )
        elif self.x < other.x and self.y > other.y and other.x - self.x == self.y - other.y:
            self._insert_neighbour(
                self.n[Dir.NE],
                other,
                lambda this, that: this.x > that.x
            )
        elif self.x < other.x and self.y < other.y and other.x - self.x == other.y - self.y:
            self._insert_neighbour(
                self.n[Dir.SE],
                other,
                lambda this, that: this.x > that.x
            )

    def throw_ball(self, d: Dir) -> tuple[Optional[Player], Dir]:        
        for _ in range(len(Dir)):
            d = d.next()
            if debug:
                print("Dir:", d)
            n = next((x for x in self.n[d] if not x.out), None)
            if n is not None:
                if debug:
                    print_board(self.players, d, self, n)
                self.out = True
                return n, d
        if debug:
            print("Finish")
            print_board(self.players, d, self, None)
        return None, Dir.E  # direction is irrelevant


def print_board(players: list[Player], d: Dir, this: Optional[Player], that: Optional[Player]) -> None:
    class bcolors:
        HEADER = '\033[95m'
        FGBLUE = '\033[94m'
        FGCYAN = '\033[96m'
        FGGREEN = '\033[92m'
        FGGRAY = '\033[90m'
        BGRED = '\033[41m'
        BGBLUE = '\033[44m'
        BGGREEN = '\033[42m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    maxx = 0
    maxy = 0
    for p in players:
        if maxx < p.x:
            maxx = p.x
        if maxy < p.y:
            maxy = p.y
    print("dir:", d)
    for y in range(maxy+1):
        for x in range(maxx+1):
            p = next((p for p in players if p.x == x and p.y == y), None)
            if p is None:
                print(" .", end="")
            elif p is this:
                print(f"{bcolors.BGGREEN}{p.idx:>2}{bcolors.ENDC}", end="")
            elif p is that:
                print(f"{bcolors.BGRED}{p.idx:>2}{bcolors.ENDC}", end="")
            elif p.out:
                print(f"{bcolors.FGGRAY}{p.idx:>2}{bcolors.ENDC}", end="")
            else:
                print(f"{p.idx:>2}", end="")
        print("")
    pass


def run_game(players: list[Player], i: int, d: Dir) -> int:
    count = 0
    p = players[i]
    while True:
        next_p, d = p.throw_ball(d)
        if next_p is None:
            break
        count += 1
        p = next_p
        d = d.invert()
    return count


def main(file_name: Optional[str]):
    if file_name is None:
        input = json.load(sys.stdin)
    else:
        with open(file_name) as fh:
            input = json.load(fh)
    for test_case in input:
        d = Dir[test_case["startingDirection"]]
        i = test_case["startingPlayer"] - 1  # index starts from 1 ???
        players: list[Player] = list()
        for idx, (x, y) in enumerate(test_case["players"]):
            new = Player(idx+1, x, y, players)
            for p in players:
                p.add_neighbour(new)
                new.add_neighbour(p)
            players.append(new)
        if debug:
            print_board(players, d, players[i], None)
        count = run_game(players, i, d)
        print(count)
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main(None)


