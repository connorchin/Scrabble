from random import shuffle

IMG_DIR = "/Users/Connor/Downloads/Scrabble/"
BOARD_SIZE = 15
WINDOW_SIZE = "1150x900"
FONT = 'Comic Sans MS'

# orientation constants
HORIZONTAL = 1
VERTICAL = 2

# LETTER_MULT[ROW][COL] -> multiplier
LETTER_MULT = {
                0: {3: 2},
                1: {5: 3},
                2: {6: 2},
                3: {0: 2, 7: 2},
                5: {1: 3, 5: 3},
                6: {2: 2, 6: 2},
                7: {3: 2}
               }

# WORD_MULT[ROW][COL] -> multiplier
WORD_MULT = {
            0: {0: 3, 7: 3},
            1: {1: 2},
            2: {2: 2},
            3: {3: 2},
            4: {4: 2},
            7: {0: 3, 7: 2}
            }

DICTIONARY = set(word.strip() for word in open('/Users/Connor/Downloads/Scrabble/big dict.txt'))
EXCEPTIONS = {"ew", "goo", "zit", "bot", "rated", "acne"}
DICTIONARY.update(EXCEPTIONS)


# bag of letters, LETTER:[VAL,COUNT]; ' ' corresponds to blank tiles
def tupToDict(instance):
    assert len(instance) == 2
    val, count = instance
    return {'value': val, 'count': count}
BAG = {
    ' ': tupToDict([0, 2]),  # 0 pt
    'A': tupToDict([1, 9]), 'E': tupToDict([1, 12]), 'I': tupToDict([1, 9]), 'O': tupToDict([1, 8]), 'U': tupToDict([1, 4]),  # 1 pt vowels
    'N': tupToDict([1, 6]), 'R': tupToDict([1, 6]), 'T': tupToDict([1, 6]), 'L': tupToDict([1, 4]), 'S': tupToDict([1, 4]),  # 1 pt consonant
    'D': tupToDict([2, 4]), 'G': tupToDict([2, 3]),  # 2 pt
    'B': tupToDict([3, 2]), 'C': tupToDict([3, 2]), 'M': tupToDict([3, 2]), 'P': tupToDict([3, 2]),  # 3 pt
    'F': tupToDict([4, 2]), 'H': tupToDict([4, 2]), 'V': tupToDict([4, 2]), 'W': tupToDict([4, 2]), 'Y': tupToDict([4, 2]),  # 4 pt
    'K': tupToDict([5, 1]),  # 5 pt
    'J': tupToDict([8, 1]), 'X': tupToDict([8, 1]),  # 8 pt
    'Q': tupToDict([10, 1]), 'Z': tupToDict([10, 1])  # 10 pt
}

# create generator object from shuffled bag
shuf = [x for x in BAG for _ in range(BAG[x]['count'])]
shuffle(shuf)
LETTERS = (i for i in shuf)

# ip, ports
IP = '127.0.0.1'
SERVER_PORT = 8888
PLAYER_PORTS = {
         1: 8889,
         2: 8890,
         3: 8891,
         4: 8892
         }

