import re
import sys
import Tkinter as tk
import tkSimpleDialog
import tkMessageBox
import tkFont
import ttk
import os
from PIL import Image, ImageTk

import imageProcessor as imgp

class kodiList(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        self.setGUI()

    def setGUI(self):
        frame = self
        sbar = tk.Scrollbar(frame, takefocus = 1, activebackground = 'blue',activerelief = tk.FLAT)
        self.listbox = listBox = tk.Listbox(frame, selectmode = tk.SINGLE, activestyle="underline",
                                            height=6, relief=tk.SUNKEN, font = self.customFont)
        sbar.config(command=listBox.yview)                    # xlink sbar and list
        listBox.config(yscrollcommand=sbar.set)               # move one moves other
        sbar.pack(side=tk.RIGHT, fill=tk.Y)                 # pack first=clip last
        sbar.bind('<Key-Left>', self.left_sbar)
        sbar.bind('<Key-Up>', lambda event, delta = -1: self.sbar_up_down(event, delta))
        sbar.bind('<Key-Down>', lambda event, delta = 1: self.sbar_up_down(event, delta))
        listBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)        # list clipped first
        # The virtual event '<<ListboxSelect>>' is used for tracking selection change
        listBox.event_add('<<Execute Option>>','<Return>','<Double-Button-1>')
        # The virtual event '<<Execute Option>>' is used for do somthing when a selection is executed
        # listBox.bind('<<ListboxSelect>>', self.handleList)
        # listBox.bind('<<Execute Option>>', self.executeOption)
        listBox.bind('<Key-Up>', self.up_event)
        listBox.bind('<Key-Down>', self.down_event)
        listBox.bind('<Key-Home>', self.home_event)
        listBox.bind('<Key-End>', self.end_event)
        listBox.bind('<Key-Right>', self.right_event)
        listBox.bind('<BackSpace>', self.back_event)
        # listBox.bind('<Button-3>',self.do_popup)
        self.sbar = sbar

    def bind(self, *args, **kwargs):
        self.listbox.bind(*args, **kwargs)

    def focus_force(self):
        self.listbox.focus_force()

    def focus_set(self):
        self.listbox.focus_set()

    def back_event(self, event):
        if self.listbox.get(0) == '..':
            self.select(0)
            self.listbox.event_generate('<<Execute Option>>')

    def home_event(self, event):
        self.select(0)
        return "break"

    def end_event(self, event):
        lsize = self.listbox.size()
        self.select(lsize - 1)
        return "break"

    def right_event(self, event):
        self.sbar.focus_force()
        self.sbar.activate('slider')
        return "break"

    def up_event(self, event):
        selItem = self.listbox.index("active")
        lsize = self.listbox.size()
        self.select((selItem + lsize -1) % lsize)
        return "break"

    def down_event(self, event):
        selItem = self.listbox.index("active")
        lsize = self.listbox.size()
        self.select((selItem + lsize + 1) % lsize)
        return "break"

    def left_sbar(self, event):
        self.listbox.focus_force()

    def sbar_up_down(self, event, delta):
        index = self.listbox.curselection()
        yoffset = self.listbox.bbox(index)[1]
        self.listbox.yview_scroll(delta, 'pages')
        index = self.listbox.nearest(yoffset)
        self.select(index)

    def select(self, index):
        self.listbox.see(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.activate(index)
        self.listbox.selection_set(index)
        self.listbox.event_generate('<<ListboxSelect>>')

    def setListContent(self, vrtFolder, selItem = 0):
        self.options = vrtFolder
        self.listbox.delete('0', 'end')
        for pos, item in enumerate(vrtFolder):
            rawLabel = self.getFormatedLabel(item)
            lcolor, itemLabel = self.formatLbxEntry(rawLabel)
            self.listbox.insert(pos, itemLabel)
            if lcolor: self.listbox.itemconfig(pos, foreground = lcolor)
        self.select(selItem)

    def formatLbxEntry(self, itemLabel):
        lcolor = None
        itemSettings = re.findall('\[COLOR (.+?)\](.+?)\[/COLOR\]', itemLabel)
        if itemSettings:
            lcolor, itemLabel = itemSettings[0]
        pattern = re.compile(r'\[(.+?)\](.+?)\[/\1\]')
        mFunc = {'UPPERCASE':'upper', 'LOWERCASE':'lower', 'CAPITALIZE':'capitalize', 'B':'encode', 'I':'encode'}
        while 1:
            match = pattern.search(itemLabel)
            if not match: break
            limI, limS = match.span()
            case = match.group(1)
            tagI, tagS = match.span(2)
            fmtText = getattr(itemLabel[tagI:tagS], mFunc[case])()
            itemLabel = itemLabel[:limI] + fmtText +itemLabel[limS:]
        return lcolor, itemLabel.replace('[CR]', '\n')

    def getFormatedLabel(self, rawLabel):
        try:
            label = rawLabel.encode('utf-8', errors='ignore')
        except:
            label = 'error'
        return label

class _kodiListBox(tkSimpleDialog.Dialog):

    def __init__(self, title='', listContent='', parent=None):
        if not parent:
            import Tkinter
            parent = Tkinter._default_root
        self.answ = None
        self.listContent = listContent or []
        tkSimpleDialog.Dialog.__init__(self, parent, title)

    def geometry(self, posStr):
        width, height = 290, 220
        posx = (self.winfo_screenwidth() - width)/2
        posy = (self.winfo_screenheight() - height)/2
        posStr = "%dx%d+%d+%d" % (width, height, posx, posy)
        tkSimpleDialog.Dialog.geometry(self, posStr)

    def body(self, master):
        self.listbox = kodiList(master)
        self.listbox.grid(row=0, rowspan=5)
        self.listbox.bind('<<Execute Option>>', self.apply)
        self.listbox.setListContent(self.listContent)
        return self.listbox


    def apply(self, event=None):
        self.answ = self.listbox.listbox.curselection()[0]

def kodiListBox(title, listContent, **kwargs):
    klb = _kodiListBox(title, listContent, **kwargs)
    return klb.answ

class waitWindow(tkSimpleDialog.Dialog):

    def __init__(self, parent, message, flagname, lock):
        self.timer = tk.StringVar()
        self.message = tk.StringVar()
        # self.icon = icon = imgp.getFontAwesomeIcon('fa-spinner', color='black', size=100)
        # self.iconPhoto = ImageTk.PhotoImage(icon)

        self.timer.set(message)
        self.message.set('Wait ')
        self.counter = 1000

        self.flagname = flagname
        self.lock = lock
        tkSimpleDialog.Dialog.__init__(self, parent, title='Wait')

    def geometry(self, posStr):
        posx = (self.winfo_screenwidth() - 200)/2
        posy = (self.winfo_screenheight() - 100)/2
        posStr = "%dx%d+%d+%d" % (200, 100, posx, posy)
        tkSimpleDialog.Dialog.geometry(self, posStr)

    def buttonbox(self):
        # self.bind("<Return>", self.ok)
        # self.overrideredirect(True)
        # self.bind("<Escape>", self.cancel)
        self.after(100, self.updateMessage)
        pass

    def updateMessage(self):
        # self.icon = self.icon.rotate(15)
        # self.iconPhoto = ImageTk.PhotoImage(self.icon)
        # self.label['image'] = self.iconPhoto
        timer = self.counter - 1
        nPoints = (1000 - timer) % 6
        self.counter = timer
        self.message.set('Wait ' + nPoints*'. ')
        with self.lock:
            flag = getattr(self.parent, self.flagname) is None
        if flag:
            self.after(100, self.updateMessage)
        else:
            self.cancel()

    def body(self, master):
        tk.Label(master, textvariable=self.timer).pack(side=tk.BOTTOM, fill=tk.X, expand=tk.YES)
        self.label = label = tk.Label(master,
                         # image = self.iconPhoto,
                         # compound=tk.LEFT,
                         textvariable=self.message,
                         anchor=tk.NW, font=('Times', '24', 'bold italic'),
                         height=1,
                         width=10)

        label.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def apply(self):
        first = int(self.e1.get())
        second = int(self.e2.get())
        print first, second # or something
        
class TreeList(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        self._sortby = None
        ttk.Treeview.__init__(self, *args, **kwargs)

        self.event_add('<<CopyEvent>>', '<Control-C>', '<Control-c>')
        self.event_add('<<MoveTo>>', '<Home>', '<End>')
        self.event_add('<<ExpandSelUpOrDown>>', '<Shift-Down>', '<Shift-Up>',
                            '<Shift-Home>', '<Shift-End>')
        self.event_add('<<SelectAll>>', '<Control-A>', '<Control-a>')
        self.event_add('<<LeftClick>>', '<Button-1>', '<Control-Button-1>', '<Shift-Button-1>')

        self.bind('<<CopyEvent>>',          self.selCopy)
        self.bind('<<ExpandSelUpOrDown>>',  self.expandSelUpOrDown)
        self.bind('<<MoveTo>>',             self.MoveTo)
        self.bind('<<LeftClick>>',          self.onLeftClick)
        self.bind('<<SelectAll>>',          lambda event: self.selection_set(self.get_children()))

    @property
    def sortby(self):
        treew = self
        sortby = self._sortby
        if sortby:
            try:
                colName = treew.heading(sortby, option='text')
            except:
                self._sortby = sortby = None
            else:
                if not any(map(colName.endswith, ('(a-z)', '(z-a)'))):
                    self._sortby = sortby = None
        return sortby

        pass

    @sortby.setter
    def sortby(self, value):
        self._sortby = value

    def selCopy(self, event=None):
        treew = self
        answ = []
        for columnId in treew.cget('columns'):
            text = treew.heading(columnId, 'text')
            if not text: break
            answ.append(text)
        nCols = len(answ)
        answ = [','.join(answ)]

        itemsSEL = treew.selection()
        for itemid in itemsSEL:
            values = treew.item(itemid, 'values')
            answ.append(','.join(values[:nCols]))
        text = '\n'.join(answ)
        treew.clipboard_clear()
        treew.clipboard_append(text)

    def expandSelUpOrDown(self,event):
        treew = self
        cursel = treew.focus()
        if event.keysym in ['Up', 'Down']:
            itemsSel = treew.selection()
            if event.keysym == 'Down':
                nxtitem = treew.next(cursel)
            else:
                nxtitem = treew.prev(cursel)
            if not nxtitem: return
            # treew.selection_toggle(nxtitem)
            if nxtitem in itemsSel:
                treew.selection_remove(cursel)
            else:
                treew.selection_add(nxtitem)
            treew.focus(nxtitem)
        elif event.keysym in ['Home', 'End']:
            toInclude = treew.get_children()
            ndx = toInclude.index(cursel)
            if event.keysym == 'End':
                pIni, pFin = ndx, len(toInclude)
            else:
                pIni, pFin = 0, ndx + 1
            treew.selection_add(toInclude[pIni:pFin])
        return 'break'

    def MoveTo(self, event=None):
        treew = self
        toInclude = treew.get_children()
        if event.keysym == 'Home':
            nxtitem = toInclude[0]
        else:
            nxtitem = toInclude[-1]
        treew.see(nxtitem)
        treew.focus(nxtitem)
        treew.selection_set(nxtitem)
        return 'break'

    def onLeftClick(self, event=None):
        treew = event.widget
        x, y = event.x, event.y
        region = self.identify_region(x, y)
        control_key = (event.state & 0x0004)
        shift_key = (event.state & 0x0001)
        if region == 'cell':
            if not (control_key or shift_key): return
            itemsSel = treew.selection()
            cursel = treew.focus()
            row = treew.identify_row(y)
            if shift_key:
                nxtitem, posFIN = sorted((cursel, row))
                while 1:
                    treew.selection_add(nxtitem)
                    if nxtitem == posFIN: break
                    nxtitem = treew.next(nxtitem)
            if control_key:
                treew.selection_toggle(row)
            treew.focus(row)
            return 'break'
        elif region == 'heading':
            iid = self.focus()
            nCol = treew.identify_column(x)
            nCol = int(nCol[1:]) - 1
            displaycolumns = treew['displaycolumns']
            if displaycolumns == ('#all',):
                displaycolumns = treew['columns']
            treeCol = displaycolumns[nCol]

            if self.sortby is not None and self.sortby == treeCol:
                    colName = treew.heading(self.sortby, option='text')
                    revFlag = colName.endswith('(a-z)')
                    colName = colName[:-5] + ('(z-a)' if revFlag else '(a-z)')
            else:
                if self.sortby:
                    colName = treew.heading(self.sortby, option='text')[:-6]
                    treew.heading(self.sortby, text=colName)
                revFlag = False
                colName =  treew.heading(treeCol, option='text') + ' (a-z)'
            treew.heading(treeCol, text=colName)
            self.sortby = treeCol
            rows = self.get_children()
            self.detach(*rows)
            rows = sorted(rows, key=lambda x: treew.item(x, option='values')[treeCol], reverse=revFlag)
            for k, iid in enumerate(rows):
                treew.move(iid, '', k)
            # self.update()
            # iid = self.focus()
            self.see(iid)
            # print '**', iid, '**'

if __name__ == '__main__':
    root = tk.Tk()
    test = 'wait'
    if test == 'KodiListBox':
        root.withdraw()
        lista = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez']
        answer = kodiListBox(title='Prueba List Box', listContent=lista)
        print answer
    if test == 'TreeList':
        import random
        random.seed(100)
        columns = ('posINI', 'posFIN', 'var0','var1','var2','var3','var4','var5')
        treelist = TreeList(root,
                            displaycolumns = '#all',
                            show = 'headings',
                            columns = columns)
        treelist.pack(fill=tk.BOTH, expand=tk.YES)
        for k, colName in enumerate(columns):
            treelist.heading(k, text = colName)
            treelist.column(colName, stretch=False)
        displaycolumns = range(1, 8)
        random.shuffle(displaycolumns)
        treelist['displaycolumns'] = displaycolumns
        for k in range(1, 50):
            linea = (random.randint(1, 100), random.randint(200, 300), random.randint(400, 500))
            linea += 5*('pos',)
            pos = treelist.insert('', 'end', values = linea)
            print pos
        root.mainloop()
    if test == 'wait':
        import threading
        kodiScriptImporterPath = os.path.abspath(os.path.join('..', 'KodiStubs\KodiImporter'))
        sys.path.append(kodiScriptImporterPath)
        import KodiScriptImporter as ksi
        importer = ksi.KodiScriptImporter()
        importer.install(True)

        lock = threading.Lock()
        root.dummy = None
        answ = waitWindow(root, 'Hola alex', 'dummy', lock)
        pass