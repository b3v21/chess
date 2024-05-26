from tkinter import *
from tkinter import ttk
from Piece import *
from PIL import ImageTk, Image
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_SQUARES = 8
SQUARE_SIZE = 80
IMAGE_RESIZE_FACTOR = 1.3

COLOR_MAP = {0: "#FBF5DE", 1: "#69923E"}


class Board(Canvas):

    def __init__(self, root: Tk, initial_board) -> None:
        super().__init__()
        root.update()

        self.image_references = {}
        self.selected_piece = None
        self.padding = (root.winfo_width() - (NUM_SQUARES * SQUARE_SIZE)) / 2
        self.image_buffer = None

        self._draw_board()
        self.current_layout = self._load_initial_positions(initial_board)
        self._current_turn = 0

    def _draw_board(self) -> None:

        self.pack(fill=BOTH, expand=1)

        for x in range(NUM_SQUARES):
            for y in range(NUM_SQUARES):
                self.create_rectangle(
                    self.padding + (x * SQUARE_SIZE),
                    self.padding + (y * SQUARE_SIZE),
                    self.padding + (x * SQUARE_SIZE) + SQUARE_SIZE,
                    self.padding + (y * SQUARE_SIZE) + SQUARE_SIZE,
                    fill=f"{COLOR_MAP[(x+y) % 2]}",
                )

    def _draw_piece(self, e: Event, piece: Piece) -> None:

        if not e:
            img = Image.open(
                f"./assets/{piece.__class__.__name__}{piece.get_colour()}.png"
            )
            resized_img = img.resize((SQUARE_SIZE, SQUARE_SIZE))
            new_img = ImageTk.PhotoImage(resized_img)

            x, y = piece.get_pos()

            self.create_image(
                self.padding + (SQUARE_SIZE * x) + SQUARE_SIZE / 2,
                self.padding + (SQUARE_SIZE * y) + SQUARE_SIZE / 2,
                image=new_img,
            )

            self.image_references[piece.get_pos()] = new_img

        else:
            if self.selected_piece:
                self.image_references[self.selected_piece.get_pos()] = None

                img = Image.open(
                    f"./assets/{self.selected_piece.__class__.__name__}{self.selected_piece.get_colour()}.png"
                )
                resized_img = img.resize((SQUARE_SIZE, SQUARE_SIZE))
                new_img = ImageTk.PhotoImage(resized_img)

                x, y = (
                    (e.x - self.padding) / SQUARE_SIZE,
                    (e.y - self.padding) / SQUARE_SIZE,
                )

                self.create_image(
                    self.padding + (SQUARE_SIZE * x),
                    self.padding + (SQUARE_SIZE * y),
                    image=new_img,
                )

                self.image_buffer = new_img

    def _select_piece(self, e: Event):

        piece_pos = (
            int((e.x - self.padding) // SQUARE_SIZE),
            int((e.y - self.padding) // SQUARE_SIZE),
        )

        candidate_piece = self.current_layout[piece_pos]
        if candidate_piece.get_colour() == self._current_turn % 2:
            self.selected_piece = candidate_piece

            print(self.selected_piece.get_legal_moves(self.current_layout))

    def _place_piece(self, e: Event):

        if self.selected_piece:
            old_x, old_y = self.selected_piece.get_pos()

            x, y = (
                int((e.x - self.padding) // SQUARE_SIZE),
                int((e.y - self.padding) // SQUARE_SIZE),
            )

            img = Image.open(
                f"./assets/{self.selected_piece.__class__.__name__}{self.selected_piece.get_colour()}.png"
            )
            resized_img = img.resize((SQUARE_SIZE, SQUARE_SIZE))
            new_img = ImageTk.PhotoImage(resized_img)

            if (x, y) in self.current_layout.keys():
                if (x, y) in self.selected_piece.get_legal_moves(self.current_layout):
                    self.create_image(
                        self.padding + (SQUARE_SIZE * x) + SQUARE_SIZE / 2,
                        self.padding + (SQUARE_SIZE * y) + SQUARE_SIZE / 2,
                        image=new_img,
                    )

                    self.image_references[x, y] = new_img
                    self.current_layout[x, y] = self.selected_piece
                    self.selected_piece.update_pos((x, y))
                    self.current_layout[old_x, old_y] = None
                    self.selected_piece = None

                    self._current_turn += 1

                else:

                    self.create_image(
                        self.padding + (SQUARE_SIZE * old_x) + SQUARE_SIZE / 2,
                        self.padding + (SQUARE_SIZE * old_y) + SQUARE_SIZE / 2,
                        image=new_img,
                    )

                    self.image_references[self.selected_piece.get_pos()] = new_img

            self.image_buffer = None
            self.print_current_layout()

    def _load_initial_positions(
        self, piece_layout: dict[tuple[int, int], tuple[Piece, int]]
    ) -> dict[tuple[int, int], Piece]:

        layout = {(x, y): None for x in range(8) for y in range(8)}

        for pos, (piece, colour) in piece_layout.items():
            if piece:
                new_piece = piece(pos, colour)
                layout[pos] = new_piece
                self._draw_piece(None, new_piece)

        return layout

    def print_current_layout(self):
        str = ""
        for y in range(8):
            for x in range(8):
                value = self.current_layout[x, y]
                str += value.__class__.__name__[0] if value else "-"
            str += "\n"
        print(str)
