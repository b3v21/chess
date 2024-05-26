from abc import ABC, abstractmethod
import itertools
import math


class Piece(ABC):

    @abstractmethod
    def __init__(self, position: tuple[int, int], colour: int):
        self.position = position
        self.colour = colour

    def get_colour(self):
        return self.colour

    def get_pos(self):
        return self.position

    def update_pos(self, new_pos):
        self.position = new_pos

    @abstractmethod
    def _remove_blocked_moves(self, check_blocked, moves):
        pass

    @abstractmethod
    def get_legal_moves(self, current_layout):
        pass


class Pawn(Piece):
    def __init__(self, position: tuple[int, int], colour: int):
        super().__init__(position, colour)

    def get_legal_moves(self, current_layout):
        x, y = self.get_pos()
        colour_factor = (
            1 if self.get_colour() == 1 else -1
        )  # Changes movement logic based on colour

        if (y == 1 and colour_factor == 1) or (y == 6 and colour_factor == -1):
            return self._remove_blocked_moves(
                [
                    (x, y + (colour_factor * 1)),
                    (x, y + (colour_factor * 2)),
                    ((x + 1), y + (colour_factor * 1)),
                    ((x - 1), y + (colour_factor * 1)),
                ],
                current_layout,
                (x, y),
            )
        else:
            return self._remove_blocked_moves(
                [
                    (x, y + (colour_factor * 1)),
                    ((x + 1), y + (colour_factor * 1)),
                    ((x - 1), y + (colour_factor * 1)),
                ],
                current_layout,
                (x, y),
            )

    def _remove_blocked_moves(self, moves, current_layout, current_pos):
        return set(
            filter(
                lambda pos: (
                    pos[0] == current_pos[0] and not current_layout[pos]
                )  # move forward
                or (
                    pos[0] != current_pos[0]
                    and current_layout[pos]
                    and current_layout[pos].get_colour()
                    != self.get_colour() 
                ),  # take diagonally
                moves,
            )
        )


class Knight(Piece):
    def __init__(self, position: tuple[int, int], colour: int):
        super().__init__(position, colour)

    def get_legal_moves(self, current_layout):
        x, y = self.get_pos()
        offset_list = list(
            set(itertools.product([-1, 1], [-2, 2]))
            | set(itertools.product([-2, 2], [-1, 1]))
        )
        moves = [(x + i, y + j) for (i, j) in offset_list]

        within_bounds_moves = set(
            filter(
                lambda pos: pos[0] >= 0
                and pos[0] <= 7
                and pos[1] >= 0
                and pos[1] <= 7
                and (
                    not current_layout[pos]
                    or self.get_colour() != current_layout[pos].get_colour()
                ),
                moves,
            )
        )

        return within_bounds_moves

    def _remove_blocked_moves(self, check_blocked, moves):
        return super()._remove_blocked_moves(check_blocked, moves)


class Bishop(Piece):
    def __init__(self, position: tuple[int, int], colour: int):
        super().__init__(position, colour)

    def get_legal_moves(self, current_layout):
        x, y = self.get_pos()
        offset_list = [
            (x + n * i, y + n * j)
            for (i, j) in itertools.product([-1, 1], [-1, 1])
            for n in range(8)
        ]

        offset_list = set(
            filter(
                lambda pos: pos[0] <= 7
                and pos[0] >= 0
                and pos[1] <= 7
                and pos[1] >= 0
                and (
                    not current_layout[pos]
                    or self.get_colour() != current_layout[pos].get_colour()
                ),
                offset_list,
            )
        )

        return self._remove_blocked_moves(offset_list, current_layout, (x, y))

    def _remove_blocked_moves(self, moves, current_layout, current_pos):
        x, y = current_pos
        invalid_moves = []

        for i, j in moves:
            xdiff = i - x
            ydiff = j - y
            xsign = 1 if xdiff > 0 else -1
            ysign = 1 if ydiff > 0 else -1

            for partial in range(1, abs(xdiff)):
                if current_layout[(x + (xsign * partial), y + (ysign * partial))]:
                    invalid_moves.append((i, j))
                    break

        return set(filter(lambda x: x not in invalid_moves, moves))


class Rook(Piece):
    def __init__(self, position: tuple[int, int], colour: int):
        super().__init__(position, colour)

    def get_legal_moves(self, current_layout):
        x, y = self.get_pos()
        moves = [(x + i, y) for i in range(1, 8 - x)]
        moves += [(x - i, y) for i in range(1, x + 1)]
        moves += [(x, y + i) for i in range(1, 8 - y)]
        moves += [(x, y - i) for i in range(1, y + 1)]

        moves = list(
            filter(
                lambda pos: not current_layout[pos]
                or self.get_colour() != current_layout[pos].get_colour(),
                moves,
            )
        )

        return self._remove_blocked_moves(moves, current_layout, (x, y))

    def _remove_blocked_moves(self, moves, current_layout, current_pos):
        x, y = current_pos
        invalid_moves = []

        for i, j in moves:
            directions = [i - x, j - y]
            abs_directions = [abs(dir) for dir in directions]
            index_diff = max(range(len(abs_directions)), key=abs_directions.__getitem__)

            sign = 1 if directions[index_diff] > 0 else -1

            for partial in range(1, max(abs_directions)):
                if index_diff:
                    if current_layout[(x, y + (sign * partial))]:
                        invalid_moves.append((i, j))
                        break
                else:
                    if current_layout[(x + (sign * partial), y)]:
                        invalid_moves.append((i, j))
                        break

        return set(filter(lambda x: x not in invalid_moves, moves))


class Queen(Rook, Bishop):
    def __init__(self, position: tuple[int, int], colour: int):
        super().__init__(position, colour)

    def get_legal_moves(self, current_layout):
        Rook.get_legal_moves(self, current_layout)
        Bishop.get_legal_moves(self, current_layout)

        return Rook.get_legal_moves(self, current_layout) | Bishop.get_legal_moves(
            self, current_layout
        )

    def _remove_blocked_moves(self, moves, current_layout, current_pos):
        x, y = current_pos
        invalid_moves = []

        for i, j in moves:
            if (i - x) == 0 or (j - y) == 0:
                directions = [i - x, j - y]
                abs_directions = [abs(dir) for dir in directions]
                index_diff = max(
                    range(len(abs_directions)), key=abs_directions.__getitem__
                )

                sign = 1 if directions[index_diff] > 0 else -1

                for partial in range(1, max(abs_directions)):
                    if index_diff:
                        if current_layout[(x, y + (sign * partial))]:
                            invalid_moves.append((i, j))
                            break
                    else:
                        if current_layout[(x + (sign * partial), y)]:
                            invalid_moves.append((i, j))
                            break
            else:
                xdiff = i - x
                ydiff = j - y
                xsign = 1 if xdiff > 0 else -1
                ysign = 1 if ydiff > 0 else -1

                for partial in range(1, abs(xdiff)):
                    if current_layout[(x + (xsign * partial), y + (ysign * partial))]:
                        invalid_moves.append((i, j))
                        break

        return set(filter(lambda x: x not in invalid_moves, moves))


class King(Piece):
    def __init__(self, position: tuple[int, int], colour: int):
        super().__init__(position, colour)

    def get_legal_moves(self, current_layout):
        x, y = self.get_pos()
        moves = [
            (x + i, y + j)
            for (i, j) in itertools.product([0, -1, 1], [0, -1, 1])
            if all(
                [
                    (x + i) >= 0,
                    (x + i) <= 7,
                    (y + j) >= 0,
                    (y + j) <= 7,
                ]
            )
        ]
        moves.remove((x, y))

        return self._remove_blocked_moves(moves, current_layout)

    def _remove_blocked_moves(self, moves, current_layout):
        return set(
            filter(
                lambda pos: (
                    not current_layout[pos]
                    or self.get_colour() != current_layout[pos].get_colour()
                ),
                moves,
            )
        )
