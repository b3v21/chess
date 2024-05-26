from tkinter import *
from tkinter import ttk
from Piece import *
from PIL import ImageTk, Image
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

NUM_SQUARES = 8
SQUARE_SIZE = 80
IMAGE_RESIZE_FACTOR = 1.3

BOARD_COLOURS = {0: "#FBF5DE", 1: "#69923E"}
COLOR_MAP = {0: "White", 1: "Black"}


class Board(Canvas):

    def __init__(self, root: Tk, initial_board) -> None:
        super().__init__()
        root.update()

        self.image_references = {}
        self.selected_piece = None
        self.padding = (root.winfo_width() - (NUM_SQUARES * SQUARE_SIZE)) / 2
        self.image_buffer = None
        self.selected_indicators = None

        self._draw_board()
        self.pieces = self._load_initial_positions(initial_board)
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
                    fill=f"{BOARD_COLOURS[(x+y) % 2]}",
                )

    def _get_piece_by_pos(self, pos):
        for piece in self.pieces:
            if piece.get_pos() == pos:
                return piece
        return False

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

        pos = (
            int((e.x - self.padding) // SQUARE_SIZE),
            int((e.y - self.padding) // SQUARE_SIZE),
        )

        # Case where user clicks to place
        if self.selected_piece:
            if not self._get_piece_by_pos(pos):
                self._place_piece(e)
                return

        candidate_piece = self._get_piece_by_pos(pos)
        if candidate_piece and candidate_piece.get_colour() == self._current_turn % 2:
            self.selected_piece = candidate_piece

            self._remove_indicators()

            self.selected_indicators = self._draw_available_moves(candidate_piece)

            # print(self.selected_piece.get_legal_moves(self.pieces))
        else:
            self._remove_indicators()

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

            # temp move piece to see if discovery occurs
            self.selected_piece.update_pos((x, y))
            check, who = self._is_check()

            # Case where a discovery check occurs
            if check and who == self._current_turn % 2:
                self._invalid_move(old_x, old_y, new_img)

            # move piece back after discovery checked
            self.selected_piece.update_pos((old_x, old_y))

            # Piece wasn't moved
            if old_x == x and old_y == y:
                self._invalid_move(old_x, old_y, new_img)

            # Move is illegal or doesn't block a check if one exists
            elif (x, y) not in self.selected_piece.get_legal_moves(
                self.pieces
            ) or self._is_check()[0]:
                self._invalid_move(old_x, old_y, new_img)

            # Move is valid
            else:
                # register taken piece
                taken_piece = self._get_piece_by_pos((x, y))
                if taken_piece:
                    self.pieces.remove(taken_piece)

                if self._is_promotion(self.selected_piece, (x, y)):
                    img = Image.open(
                        f"./assets/Queen{self.selected_piece.get_colour()}.png"
                    )
                    resized_img = img.resize((SQUARE_SIZE, SQUARE_SIZE))
                    new_img = ImageTk.PhotoImage(resized_img)

                    self.pieces.remove(self.selected_piece)
                    self.pieces.append(Queen((x, y), self._current_turn % 2))

                self.selected_piece.update_pos((x, y))
                self.image_references[x, y] = new_img

                self.create_image(
                    self.padding + (SQUARE_SIZE * x) + SQUARE_SIZE / 2,
                    self.padding + (SQUARE_SIZE * y) + SQUARE_SIZE / 2,
                    image=new_img,
                )

                self._remove_indicators()
                self.selected_piece = None
                self.image_references[old_x, old_y] = None
                self.print_current_layout()

                if self._is_checkmate():
                    lbl = Label(self, text = f"{COLOR_MAP[self._current_turn % 2]} Wins in {self._current_turn // 2 + 1} moves!")
                    lbl.place(x=self.padding+(SQUARE_SIZE*4) ,rely = 0.5, anchor=N)
                    
                self._current_turn += 1

                print("Move ", self._current_turn)

            self.image_buffer = None

    def _draw_available_moves(self, piece):

        def _check_violations(move):
            old_pos = piece.get_pos()
            piece.update_pos(move)
            check, who = self._is_check()

            if check and who == self._current_turn % 2:
                piece.update_pos(old_pos)
                return False

            piece.update_pos(old_pos)
            return True

        legal_moves = piece.get_legal_moves(self.pieces)
        legal_moves = list(filter(_check_violations, legal_moves))

        legal_move_indicators = []

        for move in legal_moves:
            legal_move_indicators.append(
                self.create_oval(
                    self.padding + (SQUARE_SIZE * move[0]) + SQUARE_SIZE * 0.45,
                    self.padding + (SQUARE_SIZE * move[1]) + SQUARE_SIZE * 0.45,
                    self.padding + (SQUARE_SIZE * move[0]) + SQUARE_SIZE * 0.55,
                    self.padding + (SQUARE_SIZE * move[1]) + SQUARE_SIZE * 0.55,
                    fill=("white" if self._current_turn % 2 == 0 else "black"),
                )
            )

        return legal_move_indicators

    def _invalid_move(self, old_x, old_y, new_img):
        self.create_image(
            self.padding + (SQUARE_SIZE * old_x) + SQUARE_SIZE / 2,
            self.padding + (SQUARE_SIZE * old_y) + SQUARE_SIZE / 2,
            image=new_img,
        )

        self.image_references[self.selected_piece.get_pos()] = new_img

    def _remove_indicators(self):
        if self.selected_indicators:
            for indicator in self.selected_indicators:
                self.delete(indicator)
            self.selected_indicators = None

    def _load_initial_positions(
        self, piece_layout: dict[tuple[int, int], tuple[Piece, int]]
    ) -> dict[tuple[int, int], Piece]:

        pieces = []

        for pos, (piece, colour) in piece_layout.items():
            if piece:
                new_piece = piece(pos, colour)
                pieces.append(new_piece)
                self._draw_piece(None, new_piece)

        return pieces

    def _is_check(self):
        for piece in self.pieces:
            for move in piece.get_legal_moves(self.pieces):
                if self._get_piece_by_pos(move).__class__.__name__ == "King":
                    return (True, self._get_piece_by_pos(move).get_colour())
        return (False, None)

    def _is_checkmate(self):
        check, who = self._is_check()
        if check and who != self._current_turn % 2:
            king = self._get_king((self._current_turn + 1) % 2)
            king_pos = king.get_pos()
            for move in king.get_legal_moves(self.pieces):
                king.update_pos(move)
                if not self._is_check()[0]:
                    king.update_pos(king_pos)
                    return False
            return True

    def _is_promotion(self, piece, new_pos):
        if piece.__class__.__name__ == "Pawn":
            if (new_pos[1] == 0 and self._current_turn % 2 == 0) or (
                new_pos[1] == 7 and self._current_turn % 2 == 1
            ):
                return True
        return False

    def _get_king(self, colour):
        for piece in self.pieces:
            if piece.__class__.__name__ == "King" and piece.get_colour() == colour:
                return piece
        return False

    def print_current_layout(self):
        str = ""
        for y in range(8):
            for x in range(8):
                value = self._get_piece_by_pos((x, y))
                if value.__class__.__name__ == "Knight":
                    str += " N "
                else:
                    str += f" {value.__class__.__name__[0]} " if value else " - "
            str += "\n"
        print(str)
