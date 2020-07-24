from Space import *
from Board import *
from Player import *
from window import *
from Game import *
import asyncio


# def main():
#     window.title("Scrabble")
#     window.geometry("1150x900")
#     p = HumanPlayer("Joe")
#     p.board.show()
#     p.gridPlayer()
#     window.mainloop()

def main():
     game = Game(hp=2)
     game.run()


if __name__ == '__main__':
     main()



