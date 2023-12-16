from collections import defaultdict
import pygame
import chess


class ChessGame:
    """
    Chess game using chess logic from python-chess library and UI from pygame.
    """

    pieces = {
        chess.Piece(chess.KING, chess.WHITE): pygame.image.load("pieces/white_king.png"),
        chess.Piece(chess.KING, chess.BLACK): pygame.image.load("pieces/black_king.png"),
        chess.Piece(chess.QUEEN, chess.WHITE): pygame.image.load("pieces/white_queen.png"),
        chess.Piece(chess.QUEEN, chess.BLACK): pygame.image.load("pieces/black_queen.png"),
        chess.Piece(chess.ROOK, chess.WHITE): pygame.image.load("pieces/white_rook.png"),
        chess.Piece(chess.ROOK, chess.BLACK): pygame.image.load("pieces/black_rook.png"),
        chess.Piece(chess.BISHOP, chess.WHITE): pygame.image.load("pieces/white_bishop.png"),
        chess.Piece(chess.BISHOP, chess.BLACK): pygame.image.load("pieces/black_bishop.png"),
        chess.Piece(chess.KNIGHT, chess.WHITE): pygame.image.load("pieces/white_knight.png"),
        chess.Piece(chess.KNIGHT, chess.BLACK): pygame.image.load("pieces/black_knight.png"),
        chess.Piece(chess.PAWN, chess.WHITE): pygame.image.load("pieces/white_pawn.png"),
        chess.Piece(chess.PAWN, chess.BLACK): pygame.image.load("pieces/black_pawn.png"),
    }

    def __resize_pieces(self):
        for piece in self.pieces:
            self.pieces[piece] = pygame.transform.scale(self.pieces[piece], (self.cell_size, self.cell_size))

    @staticmethod
    def move_to_bytes(move: chess.Move) -> bytes:
        return str(move).encode('utf-8')

    @staticmethod
    def bytes_to_move(bts: bytes) -> chess.Move:
        return chess.Move.from_uci(bts.decode('utf-8'))

    def __init__(self, width, color=None, flippy=False, local_game=True):
        self.flippy = flippy

        self.width = width
        self.cell_size = width // 8

        # initializing chess game parameters

        self.color = chess.WHITE if color is None else color
        if color is None:
            self.change_color = True
        else:
            self.change_color = False
        self.flipped = 1 - self.color

        self.turn = chess.WHITE
        self.board = chess.Board()
        self.possible_moves = defaultdict(list)
        self.update_moves()
        self._last_move = None
        self.check = False

        if local_game:
            self.second_player = 1
        else:
            self.second_player = None

        # initializing pygame

        pygame.init()
        self.screen = pygame.display.set_mode((width, width))
        pygame.display.set_caption('Chess Game')
        self.clock = pygame.time.Clock()
        self.white = (240, 236, 198)
        self.black = (199, 165, 126)
        self.selected_color = (0, 0, 255)
        self.possible_move_color = pygame.Color((236, 178, 164, 188))
        self.last_move_color = pygame.Color((174, 174, 79, 188))
        self.check_color = pygame.Color((255, 0, 0, 188))
        self.text_color = (255, 0, 0)
        self.__resize_pieces()

        self.font = pygame.font.SysFont('Comic Sans MS', bold=True, size=100)

    def get_possible_moves_at(self, square: int) -> list[chess.Move]:
        return self.possible_moves[square]

    @staticmethod
    def get_destination_squares(moves: list[chess.Move]) -> list[int]:
        return [move.to_square for move in moves]

    def coord_to_square(self, coordinates: tuple[int, int]) -> int:
        row, col = coordinates
        return chess.square(col, 7 - row) if not self.flipped else chess.square(7 - col, row)

    def get_clicked_square(self) -> int:
        pos = pygame.mouse.get_pos()
        col = pos[0] // self.cell_size
        row = pos[1] // self.cell_size
        return chess.square(col, 7 - row) if not self.flipped else chess.square(7 - col, row)

    def get_piece_at(self, coordinates: tuple[int, int]) -> chess.Piece:
        square_index = self.coord_to_square(coordinates)
        return self.board.piece_at(square_index)

    def update_moves(self):
        self.possible_moves.clear()

        for move in self.board.legal_moves:
            self.possible_moves[move.from_square].append(move)

        self.check = self.board.is_check()

    @property
    def flipped(self) -> bool:
        return (self._start, self._end, self._inc) == (0, 8, 1)

    @flipped.setter
    def flipped(self, value: bool):
        if value:
            self._start, self._end, self._inc = 0, 8, 1
        else:
            self._start, self._end, self._inc = 7, -1, -1

    @property
    def last_move(self) -> chess.Move:
        return self._last_move

    @last_move.setter
    def last_move(self, value: chess.Move):
        self._last_move = value

    def flip(self):
        self.flipped = not self.flipped

    def make_move(self, move: chess.Move):
        self.board.push(move)
        self.turn = 1 - self.turn
        self.last_move = move
        self.update_moves()
        if self.flippy:
            self.flip()

        if self.change_color:
            self.color = 1 - self.color

    def start(self):
        selected_square = None
        moved_square = None
        possible_moves = []
        moves_destinations = []
        dragging = False
        offset = 0

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    if self.board.is_game_over():
                        break

                    possible_square = self.get_clicked_square()
                    selected_piece = self.board.piece_at(possible_square)
                    if event.type == pygame.MOUSEBUTTONDOWN and self.color == self.turn and selected_piece is not None \
                            and selected_piece.color == self.turn:
                        selected_square = possible_square
                        possible_moves = self.get_possible_moves_at(possible_square)
                        moves_destinations = self.get_destination_squares(possible_moves)

                        # after clicking on piece can drag it with mouse
                        dragging = True
                        moved_square = selected_square
                        mouse_pos = pygame.mouse.get_pos()
                        square_coord = self.square_to_coord(moved_square)
                        offset = (mouse_pos[0] - square_coord[0] * self.cell_size, mouse_pos[1] - square_coord[1] *
                                  self.cell_size)
                    else:
                        dragging = False

                        # if square in possible moves than make move and update game board
                        if possible_square in moves_destinations:
                            move = possible_moves[moves_destinations.index(possible_square)]
                            self.make_move(move)
                            selected_square = None
                            moves_destinations = []
                        moved_square = None
            self.screen.fill(self.white)
            self.draw_board(selected_square, moves_destinations)
            if self.second_player is not None:
                self.show_pieces(moved_square)
                if dragging:
                    self.drag_piece(moved_square, offset)

                if self.board.is_stalemate():
                    stalemate_text = self.font.render('Draw!', True, self.text_color)
                    self.screen.blit(stalemate_text, (self.width // 2 - stalemate_text.get_width() // 2,
                                                      self.width // 2 - stalemate_text.get_height() // 2))
                elif self.board.is_checkmate():
                    result = self.board.result()
                    if "1-0" in result:
                        checkmate_text = self.font.render('White wins!', True, self.text_color)
                    else:
                        checkmate_text = self.font.render('Black wins!', True, self.text_color)
                    self.screen.blit(checkmate_text, (self.width // 2 - checkmate_text.get_width() // 2,
                                                      self.width // 2 - checkmate_text.get_height() // 2))
            pygame.display.flip()
            self.clock.tick(60)

    def draw_board(self, selected_square: int, moves_destinations: list[int]):
        for i, row in enumerate(range(self._start, self._end, self._inc)):
            for j, col in enumerate(range(7 - self._start, 7 - self._end, -self._inc)):
                cell = chess.square(col, row)
                pygame.draw.rect(self.screen, self.white if (i + j) % 2 == 0 else self.black,
                                 (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))
                if cell in moves_destinations:
                    pygame.draw.rect(self.screen, self.possible_move_color, (j * self.cell_size, i * self.cell_size,
                                                                             self.cell_size, self.cell_size))
                elif cell == selected_square:
                    pygame.draw.rect(self.screen, self.selected_color, (j * self.cell_size, i * self.cell_size,
                                                                        self.cell_size, self.cell_size))
                elif self.board.piece_at(cell) == chess.Piece(chess.KING, self.turn) and self.check:
                    pygame.draw.rect(self.screen, self.check_color, (j * self.cell_size, i * self.cell_size,
                                                                     self.cell_size, self.cell_size))
                elif self.last_move is not None and cell in (self.last_move.from_square, self.last_move.to_square):
                    pygame.draw.rect(self.screen, self.last_move_color, (j * self.cell_size, i * self.cell_size,
                                                                         self.cell_size, self.cell_size))

    def show_pieces(self, dragging_square: int):
        for i, row in enumerate(range(self._start, self._end, self._inc)):
            for j, col in enumerate(range(7 - self._start, 7 - self._end, -self._inc)):
                piece = self.board.piece_at(chess.square(col, row))
                if piece is not None and chess.square(col, row) != dragging_square:
                    self.screen.blit(self.pieces[piece], (j * self.cell_size, i * self.cell_size))

    def drag_piece(self, moved_square: int, offset: tuple[int, int]):
        piece = self.board.piece_at(moved_square)
        col, row = pygame.mouse.get_pos()
        self.screen.blit(self.pieces[piece], (col - offset[0], row - offset[1]))

    def square_to_coord(self, square: int) -> tuple[int, int]:
        row = chess.square_rank(square)
        col = chess.square_file(square)
        return (col, 7 - row) if not self.flipped else (7 - col, row)


if __name__ == '__main__':
    game = ChessGame(800)
    game.start()
