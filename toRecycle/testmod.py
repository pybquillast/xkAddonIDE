import Tkinter as tk
import tkMessageBox


class photoText(tk.Frame):
    def __init__(self, parent, content):
        tk.Frame.__init__(self, parent)
        self.bflag = False
        self.contnt = content
        self.setGUI(content)
        self.textw.insert('1.0', content)
        
    def setGUI(self, content):
        frame = self
        frame.pack()
        bottom = tk.Frame(frame)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.YES)
        self.btnVar = btnVar = tk.BooleanVar()
        self.boton = boton = tk.Checkbutton(bottom, text='Take a photo', indicatoron=0, command=self.btnCommand, variable=btnVar)
        boton.pack()

        top = tk.Frame(frame)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.scrbar = scrollbar = tk.Scrollbar(top)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        self.textw = textw = tk.Text(top, tabs=('1.5c'))
        textw.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        textw.bind('<Button-1>', self.mouseEvent)
        textw.bind('<Motion>', self.mouseEvent)

        textw.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textw.yview)

    def mouseEvent(self, event):
        x, y = event.x, event.y
        if event.num == 1:
            self.pini = (x,y)
            barx, bary = self.scrbar.get()
            print 'inicial', y, barx, bary
            self.textw.scan_mark(x, y)
            self.bflag = True
        elif event.num == 3:
            self.textw.scan_dragto(x, int(y))
            barx, bary = self.scrbar.get()
            print 'final', x, y, barx, bary, self.textw.winfo_height()
            self.bflag = False
        else:
            if self.bflag:
                # pini, pfin = self.scrbar.get()
                # x0, y0 = self.pini
                # y = y0 + (pfin - pini)*(y - y0)
                self.textw.scan_dragto(self.pini[0], y)
                # self.textw.update()
                # self.scrbar.update()
                barx, bary = self.scrbar.get()
                print 'final', y, barx, bary
        return 'break'

    def btnCommand(self):
        if self.btnVar.get():
            # tkMessageBox.showinfo('btnPush', 'Fired with TRUE')
            self.pini = self.scrbar.get()
        else:
            # tkMessageBox.showinfo('btnPush', 'Fired with False')
            pini = self.pini[0]
            pfin, pwth = self.scrbar.get()
            npages = 1.0/0.22
            pageh =  self.textw.winfo_height()/npages
            print pini, pfin
            delta = ((pfin - pini)/0.22)*pageh
            y0 = 0
            y = int(delta)
            self.textw.scan_mark(0, -min(y0, y))
            self.textw.scan_dragto(0, max(y0, y))


if __name__ == '__main__':
    # content = ''.join(['linea %s' % k for k in range(1, 101)])
    content = '\n'.join(['linea %s peor segur nod a' % k for k in range(1, 101)])

    root = tk.Tk()
    mywin = photoText(root, content)
    root.mainloop()
    pass