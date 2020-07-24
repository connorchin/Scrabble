from constants import *


def getImgDir(word_mult=1, letter_mult=1, letter='', hand=False, mid=False):
    """
    :param word_mult: space word multiplyer (1x, 2x, 3x)
    :param letter_mult: space letter multiplyer (1x, 2x, 3x)
    :param letter: letter image
    :param hand: part of hand spaces (bottom frame)
    :param mid: mid space (word multiplyer 2x) default false
    :return: image directory
    """
    if letter:
        return IMG_DIR + letter + ".ppm"
    elif letter == ' ':
        return IMG_DIR + "Blank.ppm"
    elif letter_mult > 1:
        if letter_mult == 2:
            return IMG_DIR + "DLS.ppm"
        elif letter_mult == 3:
            return IMG_DIR + "TLS.ppm"
        else:
            print("Invalid multiplier")
            exit(1)
    elif word_mult > 1:
        if word_mult == 2:
            return IMG_DIR + "MID.ppm" if mid else IMG_DIR + "DWS.ppm"
        elif word_mult == 3:
            return IMG_DIR + "TWS.ppm"
        else:
            print("invalid multiplier")
            exit(1)
    elif hand:
        # if space part of hand and has no letter, no image
        return IMG_DIR + "WhiteSpace.ppm"
    else:
        return IMG_DIR + "Blank.ppm"




def getOrientation(coords):
    if len(coords) == 1:
        return 0
    elif all([coords[x][-1] == coords[x + 1][-1] for x in range(len(coords) - 1)]):
        return VERTICAL
    elif all([coords[x][0] == coords[x + 1][0] for x in range(len(coords) - 1)]):
        return HORIZONTAL
    else:
        return -1

def validateWord(word):
    # cannot check empty strings, only single-letter words are a, i
    word = word.upper()
    if len(word) < 2:
        if word != 'a' and word != 'i':
            return False

    return word in DICTIONARY
