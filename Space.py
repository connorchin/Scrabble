from tkinter import Button
from PIL import Image, ImageTk
from utils import *
from window import *


class Space:
    PREV_BUT = None
    MOVE_HIST = list()
    PLACED_LETTERS = dict()

    def __init__(self, word_mult=1, letter_mult=1, letter='', coord=None, hand=False, mid=False):
        self.word_mult = 2 if mid else word_mult
        self.letter_mult = letter_mult
        self.letter = letter
        self.coord = coord
        self.mid = mid
        self.hand = hand
        img_dir = getImgDir(word_mult=self.word_mult,
                            letter_mult=self.letter_mult,
                            letter=self.letter,
                            hand=self.hand,
                            mid=self.mid)
        self._tile_img = None if not img_dir else ImageTk.PhotoImage(Image.open(img_dir).resize((40, 40), Image.ANTIALIAS))
        self.button = Button(topframe if not hand else bottomframe,
                             image=self._tile_img,
                             command=lambda: Space.swap(self, Space.PREV_BUT))

    @staticmethod
    def swap(current, prev, undo=False):
        """
        :param current: button just pressed
        :param prev: previously selected button
        :param undo: add to move history if not undo
        :return: nothing, just swap letters
        """
        if not prev:
            Space.PREV_BUT = current
            Space.MOVE_HIST.append((None, None))
        else:
            temp = prev.letter
            prev.letter = current.letter
            current.letter = temp

            Space._updatePlacedLetters(current)
            Space._updatePlacedLetters(prev)

            # print("current letter: {}".format(current.letter))
            # print("previous letter: {}".format(prev.letter))
            print(Space.PLACED_LETTERS)
            current.regrid()
            prev.regrid()
            if not undo:
                Space.PREV_BUT = None
                Space.MOVE_HIST[-1] = (current, prev)

    @staticmethod
    def _updatePlacedLetters(space):
        if not space.hand and space.letter:
            Space.PLACED_LETTERS[space.coord] = space.letter
        elif not space.hand:
            try:
                del Space.PLACED_LETTERS[space.coord]
            except KeyError:
                pass
        else:
            pass

    def __str__(self):
        return "Space"

    def reset(self):
        self.letter = ''
        self.regrid()

    def regrid(self):
        img_dir = getImgDir(word_mult=self.word_mult,
                            letter_mult=self.letter_mult,
                            letter=self.letter,
                            hand=self.hand,
                            mid=self.mid)
        self._tile_img = None if not img_dir else ImageTk.PhotoImage(Image.open(img_dir).resize((40, 40), Image.ANTIALIAS))
        self.button['image'] = self._tile_img


def undo():
    """
    Undo the most recent move
    :return: nothing
    """
    try:
        cur, prev = Space.MOVE_HIST.pop()
        if cur and prev:
            Space.swap(cur, prev, undo=True)
        else:
            Space.PREV_BUT = None
    except IndexError:
        pass

def validatePlacement():
    coords = list(Space.PLACED_LETTERS.keys())

    orientation = getOrientation(coords)

    return coords, orientation

def drawLetters(hand, n=7):
    for x in range(n):
        try:
            hand.append(next(LETTERS))
        except StopIteration:
            break

    return hand
