'''
Created on 23/02/2015

@author: Alex Montes Barrios
'''



import Tkinter as tk
import tkFont
import re
import Queue
import keyword

def rgbColor(red, green, blue):
    return '#%02X%02X%02X'%(red, green, blue)

PYTHONSINTAX = [
                ['pythonNumber', dict(foreground = 'IndianRed'), r'(\d+[.]*)+',re.MULTILINE],
                ['pythonFunction', dict(font = ('Consolas', 18, 'bold')), r'(?<=def)\s+(\b.+?\b)',re.MULTILINE],
                ['pythonFunction', dict(font = ('Consolas', 18, 'bold')), r'(?<=class)\s+(\b.+?\b)',re.MULTILINE],
                ['pythonKwd', dict(foreground = 'blue'), r'\b(' + '|'.join(keyword.kwlist + ['True', 'False', 'None']) + r')\b',re.MULTILINE],
                ['pythonComment', dict(foreground = 'red'), r'#.*$',re.MULTILINE],
                ['pythonMultilineString', dict(foreground = 'lime green'), r'(\"\"\"|\'\'\').*?\1|(\"\"\"|\'\'\').+',re.DOTALL],
                ['pythonString', dict(foreground = 'lime green'), r'(?<!\\)(\'|\").*?((?<!\\)\1|$)',re.MULTILINE]
                ]

XMLSINTAX = [
                ['tagnames', dict(foreground = rgbColor(63,127,127)), r'(?<=<|/)\w+',re.MULTILINE],
                ['tagdelimiters', dict(foreground = rgbColor(0,128,128)), r'(<|</|>)',re.MULTILINE],
                ['attribnames', dict(foreground = rgbColor(127, 0,127)), r'(?<= )\S+(?==)',re.MULTILINE],
                ['attribequalsign', dict(foreground = rgbColor(0,0,0)), r'(?<=\w)=(?=(\"|\'))',re.MULTILINE],
                ['attribvalues', dict(foreground = rgbColor(42,0,255)), r'(?<==)(\"|\')\S+\1',re.MULTILINE],
                ['commentcontent', dict(foreground = rgbColor(63,95,191)), r'(?<=<!--).+?(?=-->)',re.DOTALL],
                ['commentdelimiters', dict(foreground = rgbColor(63,95,191)), r'<!--|-->',re.MULTILINE],
                ['content', dict(foreground = rgbColor(0,0,0)), r'(?<=>)[^<]+(?=</)',re.MULTILINE]
                ]




class SintaxEditor(tk.Frame):

    def __init__(self, master, hrzSlider = False, vrtSlider = True):
        tk.Frame.__init__(self, master)
        self.stopFlag = False
        self.toColor = []
        self.activeCallBack = []  
        self.queue = Queue.Queue(maxsize=0)
        self.setGUI(hrzSlider, vrtSlider)
        self.editable = True
        self.contentType = self.contentSource = None
        

    def pasteFromClipboard(self, event = None):
        textw = self.textw
        try:
            data = textw.selection_get(selection = 'CLIPBOARD')
            self.setContent(data)
        except tk.TclError:
            pass
        self.formatContent()
        
    def initFrameExec(self):
        pass

    def setGUI(self,hrzSlider = False, vrtSlider = True):
        self.prompt =''
        self.cellInput = ''

        self.customFont = tkFont.Font(family = 'Consolas', size = 18)

        if vrtSlider:
            scrollbar = tk.Scrollbar(self)
            scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
            
        wrapt = tk.CHAR
        if hrzSlider:
            hscrollbar = tk.Scrollbar(self, orient = tk.HORIZONTAL)
            hscrollbar.pack(side = tk.BOTTOM, fill = tk.X)
            wrapt = tk.NONE
        
        textw = tk.Text(self, wrap = wrapt, font = self.customFont, tabs=('1.5c'))
        textw.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        if vrtSlider:
            textw.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=textw.yview)
        if hrzSlider:
            textw.config(xscrollcommand=hscrollbar.set)
            hscrollbar.config(command=textw.xview)
        

        self.textw = textw
        textw.see('end')
        textw.event_add('<<Copy>>','<Control-C>','<Control-c>')
        textw.event_add('<<Paste>>','<Control-V>','<Control-v>')
        textw.event_add('<<Cut>>','<Control-X>','<Control-x>')
        textw.event_add('<<Selall>>','<Control-A>','<Control-a>')
        textw.event_add('<<CursorlineOff>>','<Up>','<Down>','<Next>','<Prior>','<Button-1>')
        textw.event_add('<<CursorlineOn>>','<KeyRelease-Up>','<KeyRelease-Down>','<KeyRelease-Next>','<KeyRelease-Prior>','<ButtonRelease-1>')
        textw.tag_configure('cursorLine', background = 'alice blue')
        textw.tag_configure('sintaxTag')
        textw.tag_config("hyper")
        textw.tag_bind("hyper", "<Enter>", self._enter)
        textw.tag_bind("hyper", "<Leave>", self._leave)
        textw.tag_bind("hyper", "<Button-1>", self._click)        

        self.dispPrompt()
        textw.bind('<Key>', self.keyHandler)
        textw.bind('<<Copy>>', self.selCopy)
        textw.bind('<<Paste>>', self.selPaste)
        textw.bind('<<Cut>>', self.selCut)
        textw.bind('<<Selall>>',self.selAll)
        textw.bind('<<CursorlineOff>>', self.onUpPress)        
        textw.bind('<<CursorlineOn>>', self.onUpRelease)
        
    def _enter(self, event):
        self.textw.config(cursor="hand2")

    def _leave(self, event):
        self.textw.config(cursor="")
        
    def _click(self, event):
        widget = event.widget
        for tag in widget.tag_names(tk.CURRENT):
            if tag == "hyper":
                tagRange = widget.tag_prevrange(tag, tk.CURRENT)
                texto = widget.get(*tagRange)
                self.processHyperlink(texto)
                return
            
    def setHyperlinkManager(self, callbackFunction):
        self.hyperlinkManager = callbackFunction
        
    def processHyperlink(self, texto):
        if self.hyperlinkManager:
            self.hyperlinkManager(texto)
        
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
        
    def longProcess(self, baseIndex, content):
        toColor = self.toColor
        pos = 0
        anchor = baseIndex
        while self.stopFlag and self.toColor:
            matchs = [reg.search(content, pos) for tag, reg in toColor]
            if not any(matchs): 
                break
            match, k = min([(match.start(0), k) for k, match in enumerate(matchs) if match])
            tagIni = baseIndex + ' + %d chars'%matchs[k].start(0)
            tagFin = baseIndex + ' + %d chars'%matchs[k].end(0)
            self.queue.put((toColor[k][0], anchor, tagIni, tagFin))
            anchor = tagFin
            pos = matchs[k].end(0)
        self.stopFlag = False
            
    def queueConsumer(self):
        nProcess = 100
        while nProcess and not self.queue.empty():
            tagTxt, anchor, tagStart, tagEnd = self.queue.get()
            for tag in [tagname for tagname in self.textw.tag_names() if tagname.startswith('python')]:
                self.textw.tag_remove(tag, anchor, tagEnd)
            self.textw.tag_add(tagTxt, tagStart, tagEnd)
            self.textw.tag_add('sintaxTag', tagStart)
            self.textw.update()
            nProcess -= 1 
        if not self.queue.empty(): self.activeCallBack.append(self.after(50, self.queueConsumer))
        
    def setRegexPattern(self):
        sntxIndx = self.sntxIndx.get()
        return self.sintaxForColor[sntxIndx]()

    def formatContent(self,index1 = '1.0', index2 = 'end'):
        while self.activeCallBack:
            idAfter = self.activeCallBack.pop()
            self.after_cancel(idAfter)
        self.queue.queue.clear()
        if self.stopFlag:
            self.stopFlag = False
            if self.t.isAlive(): self.t.join(10)
        textw = self.textw
        content = textw.get(index1, index2)

        baseIndex = textw.index(index1)
        
        
        if not self.stopFlag:
            self.stopFlag = True
            from threading import Thread
            self.t = Thread(name="regexpThread", target=self.longProcess, args=(baseIndex, content))
            self.t.start()
            self.activeCallBack.append(self.after(50, self.queueConsumer))
        
    def getContent(self):
        textw = self.textw
        content = textw.get('1.0','end')
        return (content, self.contentType, self.contentSource)
        
    def setContent(self, contentDesc, inspos, sintaxArray = None, isEditable = True):
        content, self.contentType, self.contentSource = contentDesc
        if sintaxArray: self.sintaxisConfigure(sintaxArray)
        self.editable = isEditable
        self.__setContent__(content, inspos)
        self.onUpRelease()
        
    def setCursorAt(self, inspos, grabFocus = True):
        self.textw.mark_set(tk.INSERT, inspos)
        self.textw.see(tk.INSERT)
        if grabFocus: self.textw.focus_force()
#         self.textw.focus_force()
        
        
    def __setContent__(self, text, inspos):
        self.textw.delete('1.0','end')
        if not text: return
        if isinstance(text,basestring):
            self.textw.insert('1.0',text)
            self.formatContent()
            self.setCursorAt(inspos)
        else:
            self.textw.image_create(inspos, image = text)
            
        
    def sintaxisConfigure(self, sintaxArray):
        if self.toColor:
            for elem in self.toColor:
                self.textw.tag_remove(elem[0], '1.0', 'end')
        self.toColor = []
        sintaxArray = sintaxArray or []
        for elem in sintaxArray:
            tagName, tagCnf, tagRegEx, tagConfFlags = elem
            self.textw.tag_configure(tagName, tagCnf)
            self.toColor.append([tagName, re.compile(tagRegEx, tagConfFlags)])
        
    def selDel(self, event = None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange: textw.delete(*selRange)
        
    def selPaste(self, event = None):
        textw = self.textw
        try:
            text = textw.selection_get(selection = 'CLIPBOARD')
            baseIndex = textw.index('insert')
            textw.insert('insert', text)
        except tk.TclError:
            pass
        self.formatContent(baseIndex, 'end')
        return 'break'
        
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

    def keyHandler(self,event):
        if not self.editable and event.keysym not in  ['Left', 'Right', 'Up','Down','Next','Prior','Button-1']: 
            return 'break'        
        textw =  event.widget
        selRange = self.getSelRange()
        if event.keysym == 'Return':
            if selRange: textw.delete(*selRange)
            strInst = textw.get('insert linestart', 'insert lineend')
            self.setNextIndentation(strInst) 
            textw.insert('insert', '\n')
            self.dispPrompt()
        elif event.keysym == 'BackSpace':
            if not selRange: selRange = ("%s-1c" % tk.INSERT,)
            textw.delete(*selRange)
        elif  event.keysym == 'Delete':
            if not selRange: selRange = ("%s" % tk.INSERT,)
            textw.delete(*selRange)
        elif len(event.char) == 1:
            if selRange: textw.delete(*selRange)
            textw.insert('insert', event.char)
        else:
            return
        
        prevIndx = "%s-1c" % tk.INSERT
        if textw.tag_names(prevIndx):
            frstIndx = (textw.tag_prevrange('sintaxTag', 'insert') or ('1.0',))[0]
            textw.tag_remove('sintaxTag', frstIndx)
        frstIndx = (textw.tag_prevrange('sintaxTag', 'insert') or ('1.0',))[0] 
        self.formatContent(frstIndx, 'end')
        return "break"
    
class loggerWindow(SintaxEditor):
    def __init__(self, master):
        SintaxEditor.__init__(self, master, hrzSlider = True)

    def processLog(self, stringIn):
        self.__setContent__(stringIn, 'end')
        self.update()
        pass


class CodeEditor(SintaxEditor):
    def __init__(self, master, vrtDisc):
        SintaxEditor.__init__(self, master)
        self.kodiThreads = vrtDisc._menuthreads
        self.coder = vrtDisc.getApiGenerator()
        self.sintaxisConfigure(PYTHONSINTAX)
        
    def initFrameExec(self, refreshFlag=False):
        actThread = self.kodiThreads.threadDef
        content = self.coder.knothCode(actThread)
        contentDesc = (content, 'genfile', 'addon_module')
        self.setContent(contentDesc, inspos = "0.0", isEditable = True)
        