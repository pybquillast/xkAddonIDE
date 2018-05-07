import Tkinter as tk
import tkMessageBox
def onClick():
    tkMessageBox.showinfo('Prueba spinbox command', 'OK')
root = tk.Tk()
value = tk.StringVar()
tk.Spinbox(root, name='name', command=onClick, textvariable = value, values = ['1', '2', '3', '4']).pack()
root.mainloop()
