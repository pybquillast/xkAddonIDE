'''
Created on 13/06/2014

@author: Alex Montes Barrios
'''
import sys
import os
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import tkSimpleDialog
import ttk
import tkFont
import keyword
import pickle
import re
import urllib2
import urlparse
import webbrowser
import menuThreads

NORM_PROMPT = '>>> '
CELL_PROMPT = '... '


class PythonEditor(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        self.prompt =''
        self.cellInput = ''
        
        self.textw = tk.Text(self, font = self.customFont, tabs=('1.5c'))
        textw = self.textw 
        textw.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        textw.see('end')
        textw.event_add('<<CursorlineOff>>','<Up>','<Down>','<Next>','<Prior>','<Button-1>')
        textw.event_add('<<CursorlineOn>>','<KeyRelease-Up>','<KeyRelease-Down>','<KeyRelease-Next>','<KeyRelease-Prior>','<ButtonRelease-1>')
        textw.event_add('<<CopyEvent>>','<Control-C>','<Control-c>')
        textw.event_add('<<PasteEvent>>','<Control-V>','<Control-v>')
        textw.event_add('<<CutEvent>>','<Control-X>','<Control-x>')
        textw.event_add('<<SelAllEvent>>','<Control-A>','<Control-a>')
        
        textw.tag_configure('cursorLine', background = 'alice blue')
        textw.tag_configure('evenMatch', background = 'yellow')
        textw.tag_configure('oddMatch', background = 'red')
        textw.tag_configure('actMatch', background = 'light green')
        
        self.dispPrompt()
        textw.bind('<<CopyEvent>>', self.selCopy)
        textw.bind('<<PasteEvent>>', self.selPaste)
        textw.bind('<<CutEvent>>', self.selCut)
        textw.bind('<<SelAllEvent>>',self.selAll)
        textw.bind('<<CursorlineOff>>', self.onUpPress)        
        textw.bind('<<CursorlineOn>>', self.onUpRelease)
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        scrollbar.config(command=textw.yview)
        textw.config(yscrollcommand=scrollbar.set)
        
    def onUpPress(self, event = None):
        textw = self.textw
        textw.tag_remove('cursorLine', '1.0', 'end')
        
    def onUpRelease(self, event = None):
        textw = self.textw
        if textw.tag_ranges('sel'): return
        textw.tag_add('cursorLine', 'insert linestart', 'insert lineend + 1 chars')
        
    def getSelRange(self):
        textw = self.textw
        try:
            return textw.tag_ranges('sel')
        except tk.TclError:
            return None
        
    def formatContent(self, regexPattern, compileOp, index1 = '1.0', index2 = 'end'):
        if regexPattern == '':return 0
        opFlag = {'UNICODE':re.UNICODE, 'DOTALL':re.DOTALL, 'IGNORECASE':re.IGNORECASE, 'LOCALE':re.LOCALE, 'MULTILINE':re.MULTILINE}
        compFlags = reduce(lambda x,y: x|y,[opFlag[key]*compileOp[key].get() for key in compileOp.keys()],0)
        textw = self.textw
        content = textw.get(index1, index2)
        baseIndex = textw.index(index1)
        tagColor = ['evenMatch', 'oddMatch']
        for match in tagColor:
            textw.tag_remove(match, '1.0', 'end')
        textw.tag_remove('matchTag', '1.0', 'end')
        textw.tag_remove('actMatch', '1.0', 'end')
        k = 0
        try:
            reg = re.compile(regexPattern, compFlags)
        except:
            return k
        pos = 0
        while 1:
            match = reg.search(content, pos)
            if not match: break
            tagIni = baseIndex + ' + %d chars'%match.start(0)
            tagFin = baseIndex + ' + %d chars'%match.end(0)
            textw.tag_add(tagColor[k%2], tagIni, tagFin)
            textw.tag_add('matchTag', tagIni, tagFin)
            k += 1
            pos = match.end(0)
        return k
        
    def getContent(self, posIni = '1.0', posFin = 'end'):
        textw = self.textw
        return textw.get(posIni, posFin)
    
    def setContent(self,text):
        self.textw.delete('1.0','end')
        self.textw.insert('1.0',text)
        
    def selDel(self, event = None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange: textw.delete(*selRange)
        
    def selPaste(self, event = None):
        textw = self.textw
        try:
            text = textw.selection_get(selection = 'CLIPBOARD')
            textw.insert('insert', text)
        except tk.TclError:
            pass
        
    def selCopy(self, event = None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange:
            text = textw.get(*selRange)
            textw.clipboard_clear()
            textw.clipboard_append(text)
        return selRange

    def selCut(self, event = None):
        textw = self.textw
        selRange = self.selCopy()
        if selRange: textw.delete(*selRange)

    def selAll(self, event = None):
        textw = self.textw
        textw.tag_add('sel', '1.0', 'end')
        
    def setCustomFont(self, tFamily = "Consolas", tSize = 18):
        self.customFont.configure(family = tFamily, size = tSize)

    def dispPrompt(self):
        self.textw.insert('insert', self.prompt)
        self.textw.insert('insert', self.cellInput)

    def isIndentModeOn(self):
        return len(self.cellInput) > 0

    def setNextIndentation(self,expr):
        if len(expr):
            nTabs = len(expr) - len(expr.lstrip('\t'))
            if expr[-1] == ':': nTabs += 1
            self.cellInput = nTabs * '\t'
        else:
            self.cellInput = ''
        
    def setKeyHandler(self, objInst):
        self.textw.bind('<Key>', objInst.keyHandler)
    
class RegexTester(tk.Toplevel):
    def __init__(self, theGlobals = None):
        tk.Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.setGUI(theGlobals)
        self.xbmcThreads = menuThreads.menuThreads()
        self.activeUrl = None

    def Close(self):
        self.destroy()

    def setGUI(self, theGlobals):
        frame1 = tk.Frame(self)
        frame1.pack(fill = tk.X)
        label = tk.Label(frame1, text = "RegExPattern:")
        label.pack(side = tk.LEFT)
        
        self.regexPattern = tk.StringVar()
        self.regexPattern.trace("w", self.getPatternMatch)
        
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        entry = tk.Entry(frame1, font = self.customFont, textvariable = self.regexPattern)
        entry.pack(side=tk.LEFT, fill = tk.X, expand = 1 )
        
        self.matchLabel = tk.Label(frame1, font = self.customFont, text = "")
        self.matchLabel.pack(side = tk.LEFT)
        
        self.butNext = tk.Button(frame1, state = tk.DISABLED, font = self.customFont, text = ">", command = self.nextMatch)
        self.butNext.pack(side = tk.RIGHT)
        self.butPrev = tk.Button(frame1, state = tk.DISABLED, font = self.customFont, text = "<", command = self.prevMatch)
        self.butPrev.pack(side = tk.RIGHT)
        
        frame15 = tk.Frame(self)
        frame15.pack(fill = tk.X)
        label = tk.Label(frame15, text = "Compilation Flags:", font = self.customFont)
        label.pack(side = tk.LEFT)

        self.chkVar = {}
        chkTxt = ['UNICODE', 'DOTALL', 'IGNORECASE', 'LOCALE', 'MULTILINE']
        for elem in chkTxt:
            self.chkVar[elem] = tk.IntVar()
#             self.chkVar[elem].trace("w", self.getPatternMatch)
            chkbutt = tk.Checkbutton(frame15, text = elem, variable = self.chkVar[elem], font = self.customFont, command = self.getPatternMatch )
            chkbutt.pack(side = tk.LEFT)
        
        frame2 = tk.Frame(self)
        frame2.pack(fill = tk.BOTH, expand = 1)
        self.txtEditor = PythonEditor(frame2)
        self.txtEditor.setKeyHandler(self) 
        self.txtEditor.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        
        self.menuBuilder()

    def getPatternMatch(self, *dummy):
        regexPattern =self.regexPattern.get()
        compileOp = self.chkVar
        nMatch = self.txtEditor.formatContent(regexPattern, compileOp)
        self.txtEditor.textw.tag_remove('actMatch', '1.0', 'end')
        matchStr = ''
        if nMatch:
            posIni, posFin = self.txtEditor.textw.tag_nextrange('matchTag', '1.0')
            self.txtEditor.textw.tag_add('actMatch', posIni, posFin)
            self.txtEditor.textw.mark_set('insert', posIni)
            self.txtEditor.textw.see('insert')
            matchStr = ' 1 de ' + str(nMatch)
            self.butNext.config(state=tk.NORMAL)
            self.butPrev.config(state=tk.NORMAL)
        else:
            self.butNext.config(state=tk.DISABLED)
            self.butPrev.config(state=tk.DISABLED)
             
        self.matchLabel.config(text=matchStr)
            
    def nextMatch(self):
        selTag = self.txtEditor.textw.tag_nextrange('matchTag', 'insert + 1 char')
        matchStr = self.matchLabel['text']
        prefix, suffix = matchStr.split(' de ')
        self.txtEditor.textw.tag_remove('actMatch', '1.0', 'end')        
        if selTag != tuple():
            matchStr = ' '  + str(int(prefix) + 1) + ' de ' + suffix
        else:
            selTag = self.txtEditor.textw.tag_nextrange('matchTag', '1.0')
            matchStr = ' 1 de ' + suffix

        self.txtEditor.textw.tag_add('actMatch', *selTag)
        self.txtEditor.textw.mark_set('insert', selTag[0])
        self.txtEditor.textw.see(selTag[1])            
        self.matchLabel.config(text=matchStr)
    
    def prevMatch(self):
        selTag = self.txtEditor.textw.tag_prevrange('matchTag', 'insert - 1 char')
        matchStr = self.matchLabel['text']
        prefix, suffix = matchStr.split(' de ')
        self.txtEditor.textw.tag_remove('actMatch', '1.0', 'end')        
        if selTag != tuple():
            matchStr = ' ' + str(int(prefix) -1) + ' de ' + suffix
        else:
            selTag = self.txtEditor.textw.tag_prevrange('matchTag', 'end')
            matchStr = ' ' + suffix + ' de ' + suffix
        self.txtEditor.textw.tag_add('actMatch', *selTag)            
        self.txtEditor.textw.mark_set('insert', selTag[0])
        self.txtEditor.textw.see(selTag[0])            
        self.matchLabel.config(text=matchStr)

        
    def keyHandler(self,event):
        textw =  event.widget
        if textw == self.txtEditor.textw and event.keysym not in  ['Left', 'Right', 'Up','Down','Next','Prior','Button-1']:
            return "break"
            
    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')

    def menuBuilder(self):
        menubar = tk.Menu(self, tearoff=False)
        self.configure(menu = menubar)
        self.menuBar = {}
        menuOp = ['Get', 'View', 'ParseKnot']
        menuBar = self.menuBar
        for elem in menuOp:
            menuBar[elem] = tk.Menu(menubar, tearoff=False)
            menubar.add_cascade(label = elem, underline = 0, menu = menuBar[elem]) 

        menuOpt = []
        menuOpt.append(('command', 'File','Ctrl+F', 0, self.importFile))
        menuOpt.append(('command', 'Url','Ctrl+U', 0, self.importUrl))
        menuOpt.append(('command', 'Clipboard','Ctrl+L', 0, self.pasteFromClipboard))
        menuOpt.append(('command', 'Selected Url','Ctrl+S', 0, self.selectedURL))
        self.makeMenu('Get', menuOpt)
         
        menuOpt = []
        menuOpt.append(('command', 'New','Ctrl+S', 0, self.newParseKnot))
        menuOpt.append(('command', 'Edit','Ctrl+E', 0, self.editKnot))
        menuOpt.append(('command', 'Set Regexp','Ctrl+R', 0, self.setRegexp))
        menuOpt.append(('command', 'Set NextRegexp','Ctrl+N', 0, self.setNextRegexp))
#         menuOpt.append(('cascade', 'Saved Patterns', 0))
        self.makeMenu('ParseKnot', menuOpt)        
        
    def makeMenu(self, masterID, menuArrDesc):
        master = self.menuBar[masterID]
        for menuDesc in menuArrDesc:
            menuType = menuDesc[0]
            if menuType == 'command':
                menuType, mLabel, mAccelKey, mUnderline, mCommand =  menuDesc
                master.add(menuType,
                           label = '{:30s}'.format(mLabel),
                            accelerator = mAccelKey,
                            underline = mUnderline, 
                            command = mCommand)
            elif menuType == 'cascade':
                menuType, mLabel, mUnderline =  menuDesc
                menuLabel = masterID + '.' + mLabel.replace(' ','_')
                self.menuBar[menuLabel] = tk.Menu(master, tearoff = False)
                master.add('cascade',
                           label = '{:30s}'.format(mLabel),
                           underline = mUnderline,
                           menu = self.menuBar[menuLabel])
            else:
                master.add('separator') 

    def editKnot(self):
        if not self.activeKnot: return -1
        import ParseThreads
        ParseThreads.EditTransaction(self, self.xbmcThreads, self.activeKnot)

    def setKnotParam(self, paramStr, paramValue):
        if not self.activeKnot: return -1
        knotId = self.activeKnot
        params = self.xbmcThreads.getThreadAttr(knotId,'params')
        params[paramStr] = paramValue
                
    def setNextRegexp(self):
        self.setKnotParam('nextregexp', self.regexPattern.get())

    def setRegexp(self):
        self.setKnotParam('regexp', self.regexPattern.get())
        compflags = [key for key in self.chkVar.keys() if self.chkVar[key].get()]
        compflags = '|'.join(compflags) 
        self.setKnotParam('compflags', compflags)
        
    def newParseKnot(self):
        parseKnotId = tkSimpleDialog.askstring('Create ParseKnot', 'ParseKnot ID to create:')
        if parseKnotId:
            if self.xbmcThreads.createThread(iType = 'thread', name = parseKnotId, menuId = parseKnotId) != -1:
                self.activeKnot = parseKnotId
                self.setKnotParam('url', self.activeUrl)
                self.setRegexp()
                
    def importFile(self):
        name = tkFileDialog.askopenfilename(filetypes=[('xml Files', '*.xml'),('Text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            with open(name, 'r') as f:
                data = f.read()
#             self.regexPattern.set("")
            self.txtEditor.setContent(data)
    
    def openUrl(self, urlToOpen):
        req = urllib2.Request(urlToOpen)
        try:
            url = urllib2.urlopen(req)
        except:
            tkMessageBox.showerror('URL not Found', urlToOpen)
            data = None
        else:
            data = url.read()
            url.close()
        return data

    def importUrl(self, urlToOpen = None):
        if not urlToOpen:
            urlToOpen = tkSimpleDialog.askstring('Open URL', 'URL addres to parse:')
        if urlToOpen:
            if not urlToOpen.startswith('http://'): urlToOpen = 'http://' + urlToOpen
            self.actUrl =urlToOpen
            data = self.openUrl(urlToOpen)  
            self.txtEditor.setContent(data)
            self.activeUrl = urlToOpen
#             webbrowser.open(urlToOpen)
                
    def selectedURL(self):
        selRange = self.txtEditor.getSelRange()
        selUrl = self.txtEditor.getContent(*selRange)
        urlToOpen = urlparse.urljoin(self.actUrl, selUrl)
        self.importUrl(urlToOpen)
             
    def pasteFromClipboard(self, event = None):
        textw = self.txtEditor.textw
        try:
            data = textw.selection_get(selection = 'CLIPBOARD')
            self.txtEditor.setContent(data)
        except tk.TclError:
            pass

    def scriptTree(self, parent):
        treeview = ttk.Treeview(parent, show = 'tree', columns = ('iType','info', 'insPos'), displaycolumns = ())
        treeview.pack(fill = tk.BOTH, expand = tk.YES)
        treeview.event_add('<<myEvent>>','<Double-1>','<Return>')
        self.treeview = treeview
        self.actTreeSel = None
        return
            

if __name__ == "__main__":
    Root = tk.Tk()
    Root.withdraw()
    mainWin = RegexTester()
    mainWin.importUrl("http://www.seriales.us")
    Root.mainloop()
