import enchant
import random
import time
import tkinter as tk
import socket
from tkinter import *
from PIL import Image, ImageTk
from enum import Enum
from itertools import combinations
from constants import *
from window import *



BOARD_SIZE = 15
MID = BOARD_SIZE // 2
PREV_BUT = None
LETTERS_PLACED = 0
REMOVED = list()
PLACED_ROW = None
PLACED_COL = None
PLACED_DIR = None
MID_SET = False
BLANKS_PLACED = 0
BLANK_LETTERS = list()
TURN_COUNTER = 1
WORDS = list()
TURN_SCORE = 0



class Orientation(Enum):
    INVALID = 0
    HORIZONTAL = 1
    VERTICAL = 2

def getPerpOrientation(orientation):
    return Orientation.HORIZONTAL if orientation == Orientation.VERTICAL else Orientation.VERTICAL

class Space:
    def __init__(self, word_mult, letter_mult, mid=False):
        self.word_mult = 2 if mid else word_mult
        self.letter_mult = letter_mult
        self.letter_obj = None
        self.letter_img = None
        self.letter = ''
        self.mid = mid
        self.on_board = True
        self.tile_imgdir = self.getImgDir()
        self.tile_img = ImageTk.PhotoImage(Image.open(self.tile_imgdir).resize((40, 40), Image.ANTIALIAS))
        self.tile_button = tk.Button(topframe, image=self.tile_img if self.letter_img is None else self.letter_img, command=lambda: swap(self, PREV_BUT))
        self.letter_button = None
        self.button = self.tile_button

    def __str__(self):
        return "Space"

    def isFilled(self):
        return self.letter_img is not None and self.button['state'] != DISABLED

    def getImgDir(self):
        if self.letter_mult > 1:
            if self.letter_mult == 2:
                return "/Users/Connor/Downloads/Scrabble/DLS.ppm"
            elif self.letter_mult == 3:
                return "/Users/Connor/Downloads/Scrabble/TLS.ppm"
            else:
                print("Invalid multiplyer")
                exit(1)
        elif self.word_mult > 1:
            if self.word_mult == 2:
                if self.mid:
                    return "/Users/Connor/Downloads/Scrabble/MID.ppm"
                else:
                    return "/Users/Connor/Downloads/Scrabble/DWS.ppm"
            elif self.word_mult == 3:
                return "/Users/Connor/Downloads/Scrabble/TWS.ppm"
            else:
                print("invalid multiplyer")
                exit(1)
        else:
            return "/Users/Connor/Downloads/Scrabble/Blank.ppm"


class Letter:
    def __init__(self, letter, frame):
        self.row = None
        self.col = None
        self.letter_obj = None
        self.letter = letter
        self.frame = frame
        self.on_board = False
        if self.letter == ' ':
            img_dir = "/Users/Connor/Downloads/Scrabble/Blank.ppm"
        else:
            img_dir = "/Users/Connor/Downloads/Scrabble/" + self.letter + ".ppm"
        self.letter_img = ImageTk.PhotoImage(Image.open(img_dir).resize((40, 40), Image.ANTIALIAS))
        self.tile_img = None
        self.button = tk.Button(self.frame, image=self.letter_img, command=lambda: letterCommand(self))

    def __hash__(self):
        return hash(self.letter)

def letterCommand(self):
    swap(self, PREV_BUT)

def swap(self, other):
    global PREV_BUT
    global LETTERS_PLACED
    global PLACED_ROW
    global PLACED_COL
    global BLANKS_PLACED
    if other is not None:
        temp_img = self.letter_img
        temp_letter = self.letter
        temp_obj = self

        # only remove from grid when moving letter to empty space
        if type(other) != type(self):
            obj = self if other.__class__.__name__ == "Letter" else other
            rem = other if other.__class__.__name__ == "Letter" else self
            if obj.letter_img is not None:
                try:
                    obj.letter_obj.button.grid(row=rem.button.grid_info()['row'], column=rem.button.grid_info()['column'])
                except KeyError:
                    pass
                obj.letter_obj.on_board = False
                LETTERS_PLACED -= 1
            obj.letter_obj = rem
            obj.letter_img = rem.letter_img
            obj.letter = rem.letter
            LETTERS_PLACED += 1
            try:
                rem.button.grid_remove()
                rem.on_board = True
                if rem.letter[0] == ' ':
                    BLANKS_PLACED += 1
            except UnboundLocalError:
                pass

        # if both spaces or both letters, swap letters
        if type(other) == type(self):
            self.letter_img = other.letter_img
            self.letter = other.letter
            self.letter_obj = other.letter_obj
            other.letter_img = temp_img
            other.letter = temp_letter
            other.letter_obj = temp_obj

        # always display letter image if exists
        self.button['image'] = self.letter_img if self.letter_img is not None else self.tile_img
        other.button['image'] = other.letter_img if other.letter_img is not None else other.tile_img

        # update globals
        try:
            if self.letter_img and isinstance(self, Space):
                PLACED_ROW = int(self.button.grid_info()['row'])
                PLACED_COL = int(self.button.grid_info()['column'])
            elif other.letter_img and isinstance(other, Space):
                PLACED_ROW = int(other.button.grid_info()['row'])
                PLACED_COL = int(other.button.grid_info()['column'])
        except KeyError:
            pass

        PREV_BUT = None
    else:
        PREV_BUT = self

class Board:
    def __init__(self, size):
        self.size = size
        self.board = self.buildBoard()
        self.valid_pos = [[True if x == MID or y == MID else False for x in range(len(self.board))] for y in range(len(self.board))]
        self.letter_coord = set()

    def buildBoard(self):
        l = list()
        for i in range(self.size // 2 + 1):
            l.append(list())
            for j in range(self.size // 2 + 1):
                word_mult, letter_mult = 1, 1
                col, row = i % 7, j % 7
                if col == 0:
                    if row == 0:
                        word_mult = 3
                    elif row == 3:
                        letter_mult = 2
                elif col == 1:
                    if row == 1:
                        word_mult = 2
                    elif row == 5:
                        letter_mult = 3
                elif col == 2:
                    if row == 2:
                        word_mult = 2
                    elif row == 6:
                        letter_mult = 2
                elif col == 3:
                    if row == 0:
                        letter_mult = 2
                    elif row == 3:
                        word_mult = 2
                elif col == 4:
                    if row == 4:
                        word_mult = 2
                elif col == 5:
                    if row == 1 or row == 5:
                        letter_mult = 3
                elif col == 6:
                    if row == 2 or row == 6:
                        letter_mult = 2
                if i == 7 and j == 7:
                    l[i].append(Space(word_mult, letter_mult, mid=True))
                else:
                    l[i].append(Space(word_mult, letter_mult))
        for k in range(len(l)):
            for h in reversed(l[k][:-1]):
                l[k].append(Space(h.word_mult, h.letter_mult, mid=h.mid))

        bot = list()
        for x in range(len(l[:-1])):
            bot.append(list())
            for y in l[x]:
                bot[x].append(Space(y.word_mult, y.letter_mult, mid=y.mid))

        l += reversed(bot)

        return l

    def loadImages(self, board):
        for block_row, i in enumerate(board):
            for block_col, j in enumerate(i):
                j.button.grid(row=block_row, column=block_col)

    def clearBoard(self, complete=True):
        for x in self.board:
            for y in x:
                if not complete and y.button['state'] == DISABLED:
                    continue
                if y.letter_img is not None:
                    y.letter_img = None
                    y.letter = ''
                    y.button['image'] = y.tile_img

    def printBoard(self):
        for i in self.board:
            for j in i:
                if j.letter is not None:
                    print(j.letter, end=' ')
                elif j.word_mult > 1:
                    print(j.word_mult, end=' ')
                elif j.letter_mult > 1:
                    print(j.letter_mult, end=' ')
                else:
                    print(' ', end=' ')
            print()

    def validateBoard(self, lock_letters=True):
        global PLACED_ROW
        global PLACED_COL
        global TURN_SCORE
        global PLACED_DIR

        direction = self.validateOrientation()
        if direction == Orientation.INVALID:
            return False
        PLACED_DIR = direction
        perp_ori = Orientation.VERTICAL if direction == Orientation.HORIZONTAL else Orientation.HORIZONTAL
        start_dist = self.countInDirection(direction, -1, PLACED_ROW, PLACED_COL, score=True)
        dir_score = self.score(direction, PLACED_ROW, PLACED_COL)

        if direction == Orientation.HORIZONTAL:
            perp_score = sum([self.score(perp_ori, PLACED_ROW, x + PLACED_COL - start_dist, perp=True)
                              for x, y in enumerate(self.board[PLACED_ROW][(PLACED_COL - start_dist):])
                              if y.button['state'] != DISABLED and y.letter_img])
        else:
            perp_score = sum([self.score(perp_ori, x + PLACED_ROW - start_dist, PLACED_COL, perp=True)
                              for x, y in enumerate(self.board[(PLACED_ROW - start_dist):])
                              if y[PLACED_COL].button['state'] != DISABLED and y[PLACED_COL].letter_img])

        if dir_score < 0 or perp_score < 0:
            return False
        if TURN_COUNTER == 1 and not MID_SET:
            return False

        TURN_SCORE = dir_score + perp_score
        start = PLACED_ROW if direction == Orientation.HORIZONTAL else PLACED_COL
        if lock_letters:
            self.lockLetters(direction, start)

        return True

    def validateOrientation(self):
        horizontal = self.countInDirection(Orientation.HORIZONTAL, 1, PLACED_ROW, PLACED_COL) + self.countInDirection(Orientation.HORIZONTAL, -1, PLACED_ROW, PLACED_COL) + 1
        vertical = self.countInDirection(Orientation.VERTICAL, 1, PLACED_ROW, PLACED_COL) + self.countInDirection(Orientation.VERTICAL, -1, PLACED_ROW, PLACED_COL) + 1

        print(LETTERS_PLACED)
        if horizontal == LETTERS_PLACED:
            return Orientation.HORIZONTAL
        elif vertical == LETTERS_PLACED:
            return Orientation.VERTICAL
        else:
            return Orientation.INVALID

    def countInDirection(self, orientation, increment, r, c, score=False):
        """
        Given row, column of placed letter, find end positions of placed word
        :param orientation: Horizontal or Vertical given by enum Orientation
        :param increment: +1 or -1 depending on which direction to count to
        :param r: row
        :param c: column
        :param score: do not ignore letters already placed on the board
        :return: count: how many letters from the given row, column the ends are
        """
        global PLACED_ROW
        global PLACED_COL
        global VALID_PLACEMENT

        row_ind, col_ind = int(r), int(c)

        count = 0
        if orientation == Orientation.HORIZONTAL:
            col_ind += increment
        else:
            row_ind += increment
        while 0 < col_ind < BOARD_SIZE and 0 < row_ind < BOARD_SIZE and self.board[row_ind][col_ind].letter_img:
            if score or self.board[row_ind][col_ind].button['state'] != DISABLED:
                count += 1
            if orientation == Orientation.HORIZONTAL:
                col_ind += increment
            else:
                row_ind += increment

        return count

    # orientation: horizonal/vertical, row, col, perp: evalutating perpendicular to placed-word-orientation
    def score(self, orientation, r, c, perp=False):
        global MID_SET
        word = ""
        pt_mult = 1
        points = 0

        start_ind = self.countInDirection(orientation, -1, r, c, score=True)
        condition = orientation == Orientation.HORIZONTAL
        row = r if condition else r - start_ind
        col = c if not condition else c - start_ind

        while 0 < col < BOARD_SIZE and 0 < row < BOARD_SIZE and self.board[row][col].letter != '':
            if TURN_COUNTER == 1 and self.board[row][col].mid:
                MID_SET = True
            if self.board[row][col].word_mult > 1 and self.board[row][col].button['state'] != DISABLED:
                pt_mult = self.board[row][col].word_mult
            lt_mult = self.board[row][col].letter_mult if self.board[row][col].letter_mult > 1 and self.board[row][col].button['state'] != DISABLED else 1
            points += BAG[self.board[row][col].letter[0]][0] * lt_mult
            if self.board[row][col].letter == ' ':
                self.board[row][col].letter += BLANK_LETTERS.pop()
            word += self.board[row][col].letter[-1]
            if condition:
                col += 1
            else:
                row += 1
        print(word)
        points *= pt_mult
        # add to score if cross word length is greater than 1 or evaluating placed word
        if (perp and len(word) > 1 and validateWord(word)) or (not perp and validateWord(word)):
            return points + 50 if not perp and len(word) > 6 else points
        # add 0 if evaluating perp and word only single letter
        elif len(word) == 1:
            return 0
        # return -inf if cross word is invalid
        else:
            return float('-inf')

    def lockLetters(self, orientation, start):
        global REMOVED
        if orientation == Orientation.HORIZONTAL:
            for x, i in enumerate(self.board[start]):
                if i.isFilled():
                    if i.letter[0] == ' ':
                        i.letter_img = ImageTk.PhotoImage(Image.open("/Users/Connor/Downloads/Scrabble/" + i.letter[1] + ".ppm").resize((40, 40), Image.ANTIALIAS))
                        i.button['image'] = i.letter_img
                    REMOVED.append(i.letter[0])
                    self.updateValidPositions(start, x)
                    i.button['state'] = DISABLED
                    self.letter_coord.add((start, x, getPerpOrientation(orientation)))

        else:
            for x, i in enumerate(self.board):
                if i[start].isFilled():
                    if i[start].letter[0] == ' ':
                        i[start].letter_img = ImageTk.PhotoImage(Image.open("/Users/Connor/Downloads/Scrabble/" + i[start].letter[1] + ".ppm").resize((40, 40), Image.ANTIALIAS))
                        i[start].button['image'] = i[start].letter_img
                    REMOVED.append(i[start].letter[0])
                    self.updateValidPositions(x, start)
                    i[start].button['state'] = DISABLED
                    self.letter_coord.add((x, start, getPerpOrientation(orientation)))


    def updateValidPositions(self, r, c):
        num_spaces = 0
        iter_c1, iter_c2 = c, c
        iter_r1, iter_r2 = r, r
        while num_spaces < 7:
            if iter_r2 < BOARD_SIZE - 1:
                iter_r2 += 1
            if iter_r1 > 0:
                iter_r1 -= 1
            if iter_c2 < BOARD_SIZE - 1:
                iter_c2 += 1
            if iter_c1 > 0:
                iter_c1 -= 1
            # only set as valid if evaluating empty tile
            if self.board[r][iter_c2].letter_img is None:
                self.valid_pos[r][iter_c2] = True
            if self.board[r + 1][iter_c2].letter_img is None and num_spaces < 6:
                self.valid_pos[r + 1][iter_c2] = True
            if self.board[r - 1][iter_c2].letter_img is None and num_spaces < 6:
                self.valid_pos[r - 1][iter_c2] = True
            if self.board[r][iter_c1].letter_img is None:
                self.valid_pos[r][iter_c1] = True
            if self.board[r + 1][iter_c1].letter_img is None and num_spaces < 6:
                self.valid_pos[r + 1][iter_c1] = True
            if self.board[r - 1][iter_c1].letter_img is None and num_spaces < 6:
                self.valid_pos[r - 1][iter_c1] = True
            if self.board[iter_r2][c].letter_img is None:
                self.valid_pos[iter_r2][c] = True
            if self.board[iter_r2][c + 1].letter_img is None and num_spaces < 6:
                self.valid_pos[iter_r2][c + 1] = True
            if self.board[iter_r2][c - 1].letter_img is None and num_spaces < 6:
                self.valid_pos[iter_r2][c - 1] = True
            if self.board[iter_r1][c].letter_img is None:
                self.valid_pos[iter_r1][c] = True
            if self.board[iter_r1][c + 1].letter_img is None and num_spaces < 6:
                self.valid_pos[iter_r1][c + 1] = True
            if self.board[iter_r1][c - 1].letter_img is None and num_spaces < 6:
                self.valid_pos[iter_r1][c - 1] = True
            num_spaces += 1

        self.valid_pos[r][c] = False



class HumanPlayer:
    def __init__(self, name, letters):
        self.name = name
        self.letters = letters

    def chooseWord(self):
        s = input("Enter the word you wish to place: ")
        temp = list(s)
        for i in temp:
            if i not in temp:
                print("The word you have input is invalid. Please enter a valid word.")
                return False
            temp.remove(i)
        return validateWord(s)


class ComputerPlayer:
    def __init__(self, letters, board):
        self.letters = letters
        self.board = board

    def chooseWord(self):
        global TURN_SCORE

        hand = ''.join([x.letter for x in self.letters])
        if len(self.board.letter_coord) > 0:
            pos_words = set()
            for x in self.board.letter_coord:
                b_hand = hand + self.board.board[x[0]][x[1]].letter
                words = self.getPossibleWords(b_hand, self.board.board[x[0]][x[1]].letter)
                print(hand, b_hand, words)
                space_before = self.getSpaceAvail(x[0], x[1], -1, x[2])
                space_after = self.getSpaceAvail(x[0], x[1], +1, x[2])
                for y in words:
                    idx = y.index(self.board.board[x[0]][x[1]].letter.lower())
                    if idx > space_before:
                        continue
                    elif len(y) - idx - 1 > space_after:
                        continue
                    else:
                        word_score = getScore(y)
                        if word_score == -1:
                            continue
                        pos_words.add((y, word_score, x))
            pos_words = list(pos_words)
            scores = list()
            print(pos_words)
            for z in pos_words:
                scores.append(self.placeWord(z[0], z[2][0], z[2][1], z[2][2]))
            place = pos_words[scores.index(max(scores))]
            print(place)
            TURN_SCORE = self.placeWord(place[0], place[2][0], place[2][1], place[2][2], lock_letters=True)
            for x in self.letters:
                print(x.letter, end='')
            # tup = max(pos_words, key=lambda item:item[1])
            # print(tup)
            # self.placeWord(tup[0], tup[2][0], tup[2][1], tup[2][2])
        else:
            words = self.getPossibleWords(hand)

    def getPossibleWords(self, hand, letter_on_board, blank=False):
        words = set()
        if not blank:
            print(hand)
            for x in range(len(hand)):
                for c in combinations(hand, x + 1):
                    if letter_on_board not in c:
                        continue
                    comb = ''.join(c)
                    words.update(matchingWords(comb, DICTIONARY, words))
        else:
            for i in range(65, 91):
                temp_hand = hand + chr(i)
                for x in range(len(temp_hand)):
                    for c in combinations(temp_hand, x + 1):
                        if letter_on_board not in c:
                            continue
                        comb = ''.join(c)
                        words.update(matchingWords(comb, DICTIONARY, words))
        return words

    def getSpaceAvail(self, r, c, increment, orientation):
        row_ind = r
        col_ind = c
        count = 0
        if orientation == Orientation.HORIZONTAL:
            col_ind += increment
        else:
            row_ind += increment

        while 0 <= row_ind < BOARD_SIZE and 0 <= col_ind < BOARD_SIZE and self.board.valid_pos[row_ind][col_ind]:
            count += 1
            if orientation == Orientation.HORIZONTAL:
                col_ind += increment
            else:
                row_ind += increment

        return count

    def placeWord(self, word, r, c, orientation, lock_letters=False):
        resetGlobals()
        global PLACED_ROW
        global PLACED_COL

        PLACED_ROW = r
        PLACED_COL = c

        b_letter = self.board.board[r][c].letter
        idx = word.index(b_letter.lower())
        row_ind = r - idx if orientation == Orientation.VERTICAL else r
        col_ind = c - idx if orientation == Orientation.HORIZONTAL else c
        for i, x in enumerate(word):
            # skip letter already on board
            if i == idx:
                if orientation == Orientation.VERTICAL:
                    row_ind += 1
                else:
                    col_ind += 1
            for y in self.letters:
                if y.letter.lower() == x:
                    swap(y, self.board.board[row_ind][col_ind])
                    if lock_letters:
                        REMOVED.append(y)
                    if orientation == Orientation.VERTICAL:
                        row_ind += 1
                    else:
                        col_ind += 1
                    break

        if self.board.validateBoard(lock_letters=lock_letters):
            self.board.clearBoard(complete=False)
            if lock_letters:
                for i in REMOVED:
                    for j in self.letters:
                        if j.letter[0] == i and j.on_board:
                            self.letters.remove(j)
            return TURN_SCORE
        else:
            return float('-inf')


class Game:
    def __init__(self, board):
        self.board = board
        # self.cp = cp
        self.letters = [Letter(x, topframe) for x in BAG for _ in range(BAG[x][1])]
        name = input("Enter player name: ")
        hp_letters = list()
        cp_letters = list()
        self.hp = HumanPlayer(name, hp_letters)
        self.cp = ComputerPlayer(cp_letters, self.board)
        self.drawLetters(self.hp)
        self.drawLetters(self.cp)

        self.hp_score = 0
        self.cp_score = 0
        self.shuf = tk.Button(window, text="Shuffle", font=('Comic Sans MS', '15'), command=self.shuffleHand)
        # self.shuf.grid(row=16, column=9)
        self.shuf.place(in_=window, x=450, y=820)
        self.restart = tk.Button(window, text="Restart", font=('Comic Sans MS', '15'), command=self.takeAllLettersBack)
        # self.restart.grid(row=16, column=10)
        self.restart.place(in_=window, x=550, y=820)
        self.end_turn = tk.Button(window, text="End Turn", font=('Comic Sans MS', '15'), command=self.endTurn)
        self.end_turn.place(in_=window, x=650, y=820)
        self.word_status = tk.Label(window, text="Status: ", font=('Comic Sans Ms', '20'))
        self.word_status.place(in_=window, x=780, y=180)

    def drawLetters(self, player):
        while len(player.letters) < 7 and len(self.letters) > 0:
            c = random.choice(self.letters)
            player.letters.append(c)
            self.letters.remove(c)

    def run(self):
        # get valid position, keep prompting user until valid position inputted
        while 1:
            row = input("Enter the row of the first letter of your word: ")
            col = input("Enter the column of the first letter of your word: ")
            try:
                row = int(row)
                col = int(col)
            except ValueError:
                print("Please enter a valid position")
                continue
            if self.board.validatePosition(row, col):
                break

        # get valid direction to place word
        while 1:
            direction = input("Enter if your word is to be placed horizontally or vertically (h or v, bottomframe): ")
            if direction != 'h' or direction != 'v':
                print("Please enter a valid direction (either h or v)")
                continue
            break
        reprompt = False
        while 1:
            word = input("Enter the word you wish to place: ")
            temp = self.hp.letters
            for i in word:
                if i not in temp:
                    print("The following letter is not in your hand: %s" % i)
                    reprompt = True
                    break
                temp.remove(i)
            if reprompt:
                continue
            if not validateWord(word):
                print("Oops! The word you entered is not in the dictionary. Please try again!")
                continue

    def endTurn(self):
        global TURN_SCORE
        global TURN_COUNTER
        points_earned = tk.Label(window, text="", font=('Comic Sans MS', '20'))
        self.promptBlanks()
        if PLACED_ROW and PLACED_COL:
            if self.board.validateBoard():
                self.hp_score += TURN_SCORE
                self.displayHpScore()
                self.word_status['text'] = "Status: Valid Placement!"
                points_earned['text'] = "You've earned " + str(TURN_SCORE) + " points this turn!"
                points_earned.place(in_=window, x=780, y=230)
                for i in REMOVED:
                    for j in self.hp.letters:
                        if j.letter[0] == i and j.on_board:
                            self.hp.letters.remove(j)
                self.drawLetters(self.hp)
                self.displayHpLetters()
                self.displayTotalLetters()
                TURN_COUNTER += 1
                resetGlobals()
                self.cp.chooseWord()
                self.drawLetters(self.cp)
                self.cp_score += TURN_SCORE # change this later
                self.displayCpScore()
            else:
                self.word_status['text'] = "Status: Invalid Placement!"
                points_earned['text'] = ""
                points_earned.place(in_=window, x=780, y=230)
        else:
            pass

    def displayHpScore(self):
        name = tk.Label(topframe, text=self.hp.name + "'s Score:", font=("Comic Sans MS", '24'))
        name.grid(row=0, column=16)
        lbl = tk.Label(topframe, text=self.hp_score, font=("Comic Sans MS", '24'))
        lbl.grid(row=0, column=17)

    def displayCpScore(self):
        name = tk.Label(topframe, text="Computer Score:", font=("Comic Sans MS", '24'))
        name.grid(row=1, column=16)
        lbl = tk.Label(topframe, text=self.cp_score, font=("Comic Sans MS", '24'))
        lbl.grid(row=1, column=17)

    def displayHpLetters(self):
        hand = tk.Label(window, text="Hand:", font=("Comic Sans MS", '15'))
        hand.place(in_=window, x=0, y=820)
        index = 0
        for h in self.hp.letters:
            if not h.on_board:
                h.button.grid(row=16, column=index + 1)
                index += 1

    def displayTotalLetters(self):
        total = tk.Label(window, text="Letters Left: " + str(len(self.letters)), font=("Comic Sans MS", '24'))
        total.place(in_=window, x=780, y=300)

    def shuffleHand(self):
        random.shuffle(self.hp.letters)
        self.displayHpLetters()

    def takeAllLettersBack(self):
        for i in self.hp.letters:
            i.on_board = False
        resetGlobals()
        self.board.clearBoard(complete=False)
        self.displayHpLetters()

    def promptBlanks(self):
        global BLANKS_PLACED
        global BLANK_LETTERS
        for i in range(BLANKS_PLACED):
            popup = popupWindow(window, i + 1)
            window.wait_window(popup.top)
            BLANK_LETTERS.append(popup.value[0].upper())
        else:
            BLANK_LETTERS.reverse()
            BLANKS_PLACED = 0

    def chooseHand(self, letters):
        self.hp.letters = list()
        if len(letters) != 7:
            print("Please input 7 letters")
            exit(1)
        for i in letters:
            self.hp.letters.append(Letter(i, topframe))
            self.displayHpLetters()

class popupWindow(object):
    def __init__(self, master, num):
        top = self.top = Toplevel(master)
        self.l = Label(top, text="Choose Letter for Blank " + str(num) + " to Represent")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        self.value = self.e.get()
        self.top.destroy()

def resetGlobals():
    global LETTERS_PLACED
    global PLACED_ROW
    global PLACED_COL
    global PLACED_DIR
    global TURN_SCORE
    global REMOVED

    LETTERS_PLACED = 0
    TURN_SCORE = 0
    PLACED_ROW = None
    PLACED_COL = None
    PLACED_DIR = None
    REMOVED = list()



def validateWord(word):
    # cannot check empty strings, only single-letter words are a, i
    word = word.lower()
    if len(word) < 2:
        if word != 'a' and word != 'i':
            return False

    return word in DICTIONARY

def isSubSeq(x, y):
    temp = y
    for c in x.lower():
        if c in temp:
            temp = temp.replace(c, '')
        else:
            return False
    return True

def matchingWords(substr, words, running_set):
    return [x for x in words if len(x) == len(substr) and validateWord(x) and x not in running_set and isSubSeq(substr, x)]

def getScore(word):
    score = 0
    for x in word:
        if not 97 <= ord(x) <= 122:
            return -1
        score += BAG[x.upper()][0]

    return score + 50 if len(word) > 7 else score

def test(widget):
    widget.configure(image=ImageTk.PhotoImage(Image.open("/Users/Connor/Downloads/Scrabble/Blank.ppm").resize((40, 40), Image.ANTIALIAS)), state=DISABLED)

def main():
    b = Board(BOARD_SIZE)
    window.title("Scrabble")
    window.geometry("1150x900")
    # window.configure(bg="beige")
    b.loadImages(b.board)
    g = Game(b)
    g.displayHpScore()
    g.displayCpScore()
    g.displayHpLetters()
    g.displayTotalLetters()
    window.mainloop()


