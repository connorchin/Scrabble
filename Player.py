import random
import pickle
import socket
import threading
from tkinter import Label
from Board import *
from constants import *


class Player:
    def __init__(self, num, port, msg_len=1e6):
        self.host = 'localhost'
        self.num = int(num)
        self.port = port
        self.msg_len = int(msg_len)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.scores = dict()
        self.board = Board()
        self.letters = drawLetters(list())
        self.hand = [Space(letter=x, hand=True) for x in self.letters]


class HumanPlayer(Player):
    def __init__(self, num, port, msg_len=1e6):
        Player.__init__(self, num, port, msg_len=msg_len)

        self.player_labels = Label(displayframe, text=list(self.scores.keys()), font=(FONT, '15'))
        self.score_labels = Label(displayframe, text=list(self.scores.values()), font=(FONT, '15'))

        # initialize buttons
        self.shuffle_button = Button(bottomframe, text="Shuffle", font=(FONT, '15'), command=self._shuffle)
        self.undo_button = Button(bottomframe, text="Undo", font=(FONT, '15'), command=undo)
        self.restart_button = Button(bottomframe, text="Restart", font=(FONT, '15'), command=self._restart)
        self.endturn_button = Button(bottomframe, text="End Turn", font=(FONT, '15'), command=self._endTurn)

    def run(self):
        try:
            conn = threading.Thread(target=self._openConnection)
            conn.start()
            self._openWindow()
        except KeyboardInterrupt:
            conn.join()
            self.sock.close()

    def _openWindow(self):
        window.title("Scrabble Player: {}".format(self.num))
        window.geometry(WINDOW_SIZE)
        self._gridPlayer()
        self.board.show()

        window.mainloop()

    def _openConnection(self):
        self.sock.connect((self.host, self.port))
        try:
            while True:
                data = self.sock.recv(self.msg_len)
                if data:
                    scores, board = pickle.loads(data)
                    print("received: {}, {}".format(scores, board))
                    self.board.text_repr = board
                    self.scores = scores
                    self._gridPlayer()
                    self.board.updateRepresentation()
        except KeyboardInterrupt:
            pass

    def _gridPlayer(self):
        # display hand
        for idx, (space, letter) in enumerate(zip(self.hand, self.letters)):
            space.letter = letter
            space.regrid()
            space.button.grid(row=BOARD_SIZE + 1, column=idx + 1)

        self.player_labels['text'] = list(self.scores.keys())
        self.score_labels['text'] = list(self.scores.values())
        self.player_labels.grid(row=0)
        self.score_labels.grid(row=1)

        # display player controls
        self.shuffle_button.grid(row=BOARD_SIZE + 1, column=9)
        self.undo_button.grid(row=BOARD_SIZE + 1, column=10)
        self.restart_button.grid(row=BOARD_SIZE + 1, column=11)
        self.endturn_button.grid(row=BOARD_SIZE + 1, column=12)


    def _shuffle(self):
        random.shuffle(self.hand)
        for idx, space in enumerate(self.hand):
            space.button.grid(row=BOARD_SIZE + 1, column=idx + 1)

    def _restart(self):
        self.board.resetTurn()
        self._gridPlayer()

    def _endTurn(self):
        score = self.board.validateBoard()
        if score > 0:
            self.scores[self.num] += score
            self._drawFull()
            Space.PREV_BUT = None
            Space.MOVE_HIST = list()
            Space.PLACED_LETTERS = dict()

            # send board to server
            package = (self.scores, self.board.text_repr)
            print("sending: {}".format(package))
            data = pickle.dumps(package)
            self.sock.send(data)



    def _drawFull(self):
        self.letters = [x.letter for x in self.hand if x.letter]
        self.letters = drawLetters(self.letters, n=(7 - len(self.letters)))
        self._gridPlayer()


