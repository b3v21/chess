from Model import *


class Controller:
    def __init__(self, piece_encoding):

        root = Tk()
        root.title("Chess")
        root.minsize(400, 400)
        root.minsize(800, 800)
        root.geometry("300x300+50+50")

        self.init_piece_encoding = piece_encoding

        board = Board(root, self.init_piece_encoding)

        board.bind(
            "<Button-1>",
            board._select_piece,
        )

        board.bind(
            "<B1-Motion>",
            lambda event: board._draw_piece(event, None),
        )

        board.bind(
            "<ButtonRelease-1>",
            board._place_piece,
        )

        root.mainloop()
