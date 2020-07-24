from tkinter import Tk, Frame

window = Tk()

# board frame
topframe = Frame(window)
topframe.grid(row=0, column=0)

# hand frame
bottomframe = Frame(window)
bottomframe.grid(row=1, column=0)

# display frame
displayframe = Frame(window)
displayframe.grid(row=0, column=1)
