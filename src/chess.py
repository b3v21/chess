import os
import sys
from Controller import *

if len(sys.argv) == 1 or sys.argv[1] == "-d":
    PIECE_ENCODING = {
        (0, 0): (Rook, 1),
        (1, 0): (Knight, 1),
        (2, 0): (Bishop, 1),
        (3, 0): (Queen, 1),
        (4, 0): (King, 1),
        (5, 0): (Bishop, 1),
        (6, 0): (Knight, 1),
        (7, 0): (Rook, 1),
        (0, 7): (Rook, 0),
        (1, 7): (Knight, 0),
        (2, 7): (Bishop, 0),
        (3, 7): (Queen, 0),
        (4, 7): (King, 0),
        (5, 7): (Bishop, 0),
        (6, 7): (Knight, 0),
        (7, 7): (Rook, 0),
    }

    for x in range(8):
        for y in [1, 6]:
            PIECE_ENCODING[(x, y)] = (Pawn, y % 2)

    for x in range(8):
        for y in range(2, 6):
            PIECE_ENCODING[(x, y)] = (None, 0)


controller = Controller(PIECE_ENCODING)
