from Player import *
from Board import *
from constants import *
from copy import deepcopy
import threading


class Game:
    def __init__(self, hp=1, cp=0, port=SERVER_PORT, msg_len=1e6):
        self.port = port
        self.msg_len = int(msg_len)
        self.host = 'localhost'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.hp = list()
        self.cp = list()
        self.num_players = hp + cp
        self.text_board = ['' for _ in range(BOARD_SIZE * BOARD_SIZE)]
        self.turn = 0
        self.scores = {x: 0 for x in range(self.num_players)}

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.num_players)
        threads = list()
        connections = list()
        player_num = 0
        try:
            while True:
                conn, addr = self.sock.accept()
                client = threading.Thread(target=self._communicate, args=(conn, player_num))
                self.scores[player_num] = 0
                client.start()
                threads.append(client)
                connections.append(conn)
                player_num += 1
        except KeyboardInterrupt:
            for thread, conn in zip(threads, connections):
                thread.join()
                conn.close()
            self.sock.close()

    def _communicate(self, conn, player):
        print("Starting thread for player {}".format(player))
        local_board = deepcopy(self.text_board)
        package = (self.scores, self.text_board)
        conn.sendall(pickle.dumps(package))
        print("sending to player {}: {}".format(player, package))

        while True:
            # send update to client
            if local_board != self.text_board:
                local_board = deepcopy(self.text_board)
                package = (self.scores, self.text_board)
                conn.sendall(pickle.dumps(package))
                print("sending to player {}: {}".format(player, package))
            # send update board to client, wait for response
            if self.turn == player:
                print("Player {} turn".format(player))

                # update scores, board
                package = (self.scores, self.text_board)
                conn.sendall(pickle.dumps(package))
                print("sending to player {}: {}".format(player, package))

                # wait for turn score, board
                data = conn.recv(self.msg_len)
                scores, board = pickle.loads(data)
                print("received: {}, {}".format(scores, board))

                # update player score, board
                self.scores = scores
                self.text_board = board
                self.turn = (self.turn + 1) % self.num_players
