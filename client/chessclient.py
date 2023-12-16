import socket
import threading
import chess
import chessgame as game


class ChessClient(game.ChessGame):
    """
    Chess game client. Represents second (black) player.
    """

    def __init__(self, width, host, port, flippy=False):

        # set game properties and ui
        super().__init__(width, chess.BLACK, flippy)

        # connect to server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.second_player = self.socket
        self.flipped = not self.color

        thread = threading.Thread(target=self.handle_host)
        thread.start()

        super().start()
        super().flip()

    def handle_host(self):
        while True:
            move = self.bytes_to_move(self.second_player.recv(1024))
            super().make_move(move)

    def make_move(self, move: chess.Move):
        super().make_move(move)
        self.second_player.send(self.move_to_bytes(move))

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        """Close the socket when cleaning up."""
        if hasattr(self, 'socket') and self.socket:
            self.socket.close()


if __name__ == '__main__':
    ChessClient(800, '127.0.0.1', 5000)