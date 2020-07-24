from Player import *


def main():
    num = input("Enter player number: ")
    player = HumanPlayer(num, 8888)
    player.run()

if __name__ == '__main__':
    main()