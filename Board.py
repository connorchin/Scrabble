from Space import *
from constants import *
from utils import validateWord
from math import ceil



class Board:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.board = self._buildBoard()
        self.text_repr = ['' for _ in range(BOARD_SIZE * BOARD_SIZE)]

    def _buildBoard(self):
        l = list()
        mid_coor = ceil(self.size / 2)
        # build first quadrant
        for i in range(mid_coor):
            l.append(list())
            for j in range(mid_coor):
                try:
                    letter_mult = LETTER_MULT[i][j]
                except KeyError:
                    letter_mult = 1
                try:
                    word_mult = WORD_MULT[i][j]
                except KeyError:
                    word_mult = 1

                if i == 7 and j == 7:
                    l[i].append(Space(word_mult, letter_mult, coord=(i, j), mid=True))
                else:
                    l[i].append(Space(word_mult, letter_mult, coord=(i, j)))
        # build second quadrant
        for k in range(len(l)):
            for col, h in zip(range(mid_coor, BOARD_SIZE), reversed(l[k][:-1])):
                l[k].append(Space(h.word_mult, h.letter_mult, coord=(k, col), mid=h.mid))

        # build bottom half
        bot = list()
        for row, x in zip(range(BOARD_SIZE - 1, mid_coor - 1, -1), range(len(l[:-1]))):
            bot.append(list())
            for y in l[x]:
                _, col = y.coord
                bot[x].append(Space(y.word_mult, y.letter_mult, coord=(row, col), mid=y.mid))

        # coalesce two halves
        l += reversed(bot)

        # flatten to 1D list
        flatten = [space for row in l for space in row]
        return flatten

    def resetTurn(self):
        for row, col in list(Space.PLACED_LETTERS.keys()):
            space = self.board[row * BOARD_SIZE + col]
            space.reset()
        Space.PLACED_LETTERS = dict()

    def validateBoard(self):
        coords, orientation = validatePlacement()
        score = self._score(coords, orientation)
        if score > 0:
            self._lockLetters(coords)
        return score

    def _lockLetters(self, coordinates):
        for row, col in coordinates:
            space = self.board[row * BOARD_SIZE + col]

            # update text representation
            self.text_repr[row * BOARD_SIZE + col] = space.letter
            space.button['state'] = "disable"

    def _score(self, coordinates, orientation):
        score = 0
        if len(coordinates) == 0:
            return 0
        if orientation == -1:
            return -1

        # single letter
        if orientation == 0:
            r, c = coordinates[0]
            if self.board[r * BOARD_SIZE + c + 1].letter or self.board[r * BOARD_SIZE + c - 1].letter:
                orientation = HORIZONTAL
            else:
                orientation = VERTICAL

        word = self._getWord(coordinates[0], orientation)
        if not validateWord(word):
            return -1

        score += self._getScore(word, coordinates=coordinates)
        print(word)
        print(score)

        perp_orientation = VERTICAL if orientation == HORIZONTAL else HORIZONTAL
        for coord in coordinates:
            word = self._getWord(coord, perp_orientation)
            if len(word) > 1:
                if not validateWord(word):
                    return -1
                print(word)
                print(self._getScore(word, coordinates=[coord]))
                score += self._getScore(word, coordinates=[coord])
        print(score)
        return score

    def _getWord(self, coordinate, orientation):
        """
        :param coordinate: tuple (row, col)
        :param orientation: VERTICAL or HORIZONTAL (assumed to be valid)
        :return: word in orientation
        """
        row, col = coordinate
        step = 1 if orientation == HORIZONTAL else BOARD_SIZE
        idx = row * BOARD_SIZE + col
        word = ''

        # form first half
        while idx >= 0 and idx % BOARD_SIZE >= 0 and self.board[idx].letter:
            word += self.board[idx].letter
            idx -= step

        idx = row * BOARD_SIZE + col + step
        word = word[::-1]

        # add second half
        while idx < BOARD_SIZE * BOARD_SIZE and idx % BOARD_SIZE > 0 and self.board[idx].letter:
            word += self.board[idx].letter
            idx += step
        print(word)
        return word

    def _getScore(self, word, coordinates):
        """
        :param word: created word (assume valid)
        :param coordinates: list of tuples (row, col) assume valid orientation
        :return: score
        """
        score = 0
        word_mult = 1
        word = list(word)
        seen = dict()

        # calculate score of placed letters (specified by coordinates)
        for row, col in coordinates:
            space = self.board[row * BOARD_SIZE + col]

            # add instance of letter to seen, increment score
            seen[space.letter] = 1 if space.letter not in seen else seen[space.letter] + 1
            score += BAG[space.letter]['value'] * space.letter_mult

            # assign word multiplier if applicable
            if space.word_mult > 1:
                word_mult = space.word_mult

        # calculate score of remaining letters in word
        for letter in word:
            if letter not in seen:
                score += BAG[letter]['value']
            else:
                seen[letter] -= 1
                if seen[letter] == 0:
                    del seen[letter]

        score *= word_mult
        return score

    def updateRepresentation(self):
        for space, letter in zip(self.board, self.text_repr):
            space.letter = letter
            space.regrid()
            # disable button if letter exists
            space.button['state'] = "disabled" if space.letter else "normal"

    def show(self):
        for block_row in range(BOARD_SIZE):
            for block_col in range(BOARD_SIZE):
                self.board[block_row * BOARD_SIZE + block_col].button.grid(row=block_row, column=block_col)
