import socket
import sys
import threading
import chess

sys.path.append("D:/Python/Projects/WebChess")

import chessgame as game


class ChessHost(game.ChessGame):

    def __init__(self, width, host, port, color=chess.WHITE, flippy=False):
        super().__init__(width, color, flippy)

        # initialize server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.second_player = None
        self.flipped = not self.color

        thread = threading.Thread(target=self.handle_client)
        thread.start()

        super().start()

    def make_move(self, move: chess.Move):
        super().make_move(move)
        self.second_player.send(self.move_to_bytes(move))

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        """Close the socket when cleaning up."""
        if hasattr(self, 'socket') and self.socket:
            self.socket.close()

    def handle_client(self):
        self.socket.listen(1)
        self.second_player = self.socket.accept()[0]

        while True:
            move = self.bytes_to_move(self.second_player.recv(1024))
            super().make_move(move)


if __name__ == '__main__':
    ChessHost(800, '127.0.0.1', 5000, chess.WHITE)
