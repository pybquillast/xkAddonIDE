'''
Created on 5/03/2014

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
        textw.tag_configure('pythonKwd', foreground = 'blue')
        textw.tag_configure('pythonString', foreground = 'lime green')
        textw.tag_configure('pythonComment', foreground = 'grey')
        textw.tag_configure('cursorLine', background = 'alice blue')

        self.dispPrompt()
        textw.bind('<Key>', self.keyHandler)
        textw.bind('<Control-C>', self.selCopy)
        textw.bind('<Control-V>', self.selPaste)
        textw.bind('<Control-X>', self.selCut)
        textw.bind('<Control-A>',self.selAll)
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
        
    def formatContent(self,index1 = '1.0', index2 = 'end'):
        textw = self.textw
        content = textw.get(index1, index2)
        toColor = []
        toColor.append(('pythonKwd',r'\b(' + '|'.join(keyword.kwlist) + r')\b')) 
        toColor.append(('pythonString', r'([\'\"]{3}|[\'\"]).*?\1'))
        toColor.append(('pythonComment', '#.*'))        
        baseIndex = textw.index(index1)
        
        for tagToColor, rePattern in  toColor:
            if tagToColor != 'pythonString':
                reg = re.compile(rePattern)
            else:
                reg = re.compile(rePattern, re.DOTALL)
            pos = 0
            while 1:
                match = reg.search(content, pos)
                if not match: break
                tagIni = baseIndex + ' + %d chars'%match.start(0)
                tagFin = baseIndex + ' + %d chars'%match.end(0)
                textw.tag_add(tagToColor, tagIni, tagFin)
                pos = match.end(0)
        
        
        
    def getContent(self):
        textw = self.textw
        return textw.get('1.0','end')
    
    def setContent(self,text):
        self.textw.delete('1.0','end')
        self.textw.insert('1.0',text)
        self.formatContent()
        
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
            
    
        
    def keyHandler(self,event):
        textw =  event.widget
        if event.keysym == 'Return':
            strInst = textw.get('insert linestart', 'insert lineend')
            self.setNextIndentation(strInst) 
            textw.insert('insert', '\n')
            self.dispPrompt()
            return "break"
        if event.keysym in 'abcdefghijklmnopqrstuvwxyz':
            textw.insert('insert',event.keysym)            
            word = textw.get('insert -1 chars wordstart', 'insert -1 chars wordend')
            textw.tag_remove('pythonKwd', 'insert -1 chars wordstart', 'insert -1 chars wordend')
            if keyword.iskeyword(word):
                textw.tag_add('pythonKwd', 'insert -1 chars wordstart', 'insert -1 chars wordend')
            return "break"

class PythonFrontEnd(tk.Frame):
    def __init__(self, master, theGlobals=None):
        tk.Frame.__init__(self, master)
        frontEndComm = dict(cls = self._clear, changeFont=self.setCustomFont)
        if theGlobals == None: theGlobals = {}
        theGlobals.update(frontEndComm)
        self._globals = theGlobals
        self.outputBuffer = []
        self.inCommands = []
        self.inCommandsPos = 0
        self.prompt = NORM_PROMPT
        self.cellInput = ''
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        
        self.textw = tk.Text(self, font = self.customFont)
        text = self.textw 
        text.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)  
        text.bind('<Key>', self.keyHandler)
        text.tag_configure('error', foreground = 'red')
        text.tag_configure('output', foreground = 'blue')
        text.tag_configure('prompt', foreground ='green')
        self.dispPrompt()
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        scrollbar.config(command=text.yview)
        text.config(yscrollcommand=scrollbar.set)

        
    def setCustomFont(self, tFamily = "Consolas", tSize = 18):
        self.customFont.configure(family = tFamily, size = tSize)
        
    def dispPrompt(self):
        self.textw.insert(tk.END, self.prompt, ('prompt',))
        self.textw.insert(tk.END, self.cellInput)
        
    def _clear(self):
        self.textw.delete('1.0', 'end')
        
    def clear(self):
        self._clear()
        self.dispPrompt()
        
    def keyHandler(self,event):
        if not (event.keysym in ['Return', 'Up', 'Down', 'Escape', 'Home']):return
        textw =  event.widget
        if event.keysym == 'Return': 
            textw.mark_set(tk.INSERT, 'end -1 chars')
        if event.keysym == 'Home':
            strLine = textw.get('insert linestart', 'insert lineend')
            homePos = textw.index('insert linestart +%s chars'%len(self.prompt))
            if strLine.find(self.prompt) == 0:
                homePos = textw.index('insert linestart +%s chars'%len(self.prompt))
                textw.mark_set('insert', homePos)
                return 'break'
        if(textw.index('insert lineend') == textw.index('end -1 chars')):
            if event.keysym == 'Return':
                strInst = event.widget.get('end -1 lines', 'end')
                sfilter = self.prompt.strip('\t')+'\n'
                expr = self.getPythonExpr(strInst.strip(sfilter)) 
                event.widget.insert('end', '\n')
                self.runPythonExpr(expr)
                self.dispPrompt()
                textw.see('end')
                return "break"
            elif event.keysym == 'Up':
                if int(textw.index('insert').split('.')[1]) < len(self.prompt): return
                self.inCommandsPos = max(-len(self.inCommands), self.inCommandsPos - 1) 
            elif event.keysym == 'Down':
                self.inCommandsPos = min(0, self.inCommandsPos + 1)
            elif event.keysym == 'Escape':
                self.inCommandsPos = 0
            expr = ''
            if self.inCommandsPos != 0:expr = self.inCommands[self.inCommandsPos]
#             en este punto la instruccion deberia ser 
#             textw.replace('end -1 lines', 'end', '\n')
#             pero python deja de funcionar
            textw.delete('end -1 lines', 'end')
            textw.insert('end', '\n')
            self.dispPrompt()
            textw.insert('end',expr)
            return "break"

    def isCellModeOn(self):
        return self.prompt.find(CELL_PROMPT) == 0
        
    def getPythonExpr(self,expr):
        """Makes it easier to build consoles.
        """
        self.inCommands.append(expr)
        if (len(expr) and expr[-1] == ':') or self.isCellModeOn():
            self.inCommandsPos += 1
            if len(expr):
                nTabs = len(expr) - len(expr.lstrip('\t'))
                if expr[-1] == ':': nTabs += 1
                self.cellInput = nTabs * '\t'
                self.prompt = CELL_PROMPT
                return ''
            self.prompt = NORM_PROMPT
            self.cellInput = ''
            self.inCommands.pop()
            expr = ''            
            for n in range(-1, -self.inCommandsPos, -1):
                expr =  self.inCommands[n] + '\n' + expr
        self.inCommandsPos = 0
        return expr

            
    def runPythonExpr(self,expr):
        """Makes it easier to build consoles.
        """
        if expr == '': return
        self.beginTrappingOutput()
        colorToApply = ('output',)        
        try: 
            # first, we assume it is an expression
            result_object = eval(str(expr), self._globals)
            if result_object == None:
                result_object = ''
            else:
                result_object = str(result_object) + '\n'
        except:
            #failing that, try to execute it
            try:
                exec(str(expr), self._globals)
            except Exception as err:
                print ("Unexpected error:", err)
                colorToApply = ('error',)
            result_object = ''
        if result_object == '': result_object = self.endTrappingOutput()
        result_object = str(result_object)
        self.textw.insert('end -1 chars', result_object, *colorToApply)

    def beginTrappingOutput(self):
        self.outputBuffer = []
        self.old_output = sys.stdout
        sys.stdout = self
    
    def write(self, expr):
        """ this is an internal utility used to trap the output.
        add it to a list of strings - this is more efficient
        than adding to a possibly very long string."""
        self.outputBuffer.append(str(expr))

    def getStandardOutput(self):
        "Hand over output so far, and empty the buffer"
        text = ''.join(self.outputBuffer)
        self.outputBuffer = []
        return text

    def endTrappingOutput(self):
        sys.stdout = self.old_output
        # return any more output
        return self.getStandardOutput()
        

class xbmcMenu(tk.Toplevel):
    def __init__(self, theGlobals = None):
        tk.Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.setGUI(theGlobals)
        self.parseThreads={}

    def setGUI(self, theGlobals):
        m1 = tk.PanedWindow(self, sashrelief = tk.SUNKEN, bd = 10)
        m1.pack(fill=tk.BOTH, expand=tk.YES)

        self.pyEditor = PythonEditor(m1)        
        self.scriptTree(m1)
        
        m1.add(self.treeview)
        m1.add(self.pyEditor)
                
        self.menuBuilder()
        
    def menuBuilder(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 12)
        menubar = tk.Menu(self, tearoff=False, postcommand = self.menuConf)
        self.configure(menu = menubar)
        self.menuBar = {}
        menuOp = ['File', 'Edit', 'View', 'Insert', 'Run']
        menuBar = self.menuBar
        for elem in menuOp:
            menuBar[elem] = tk.Menu(menubar, tearoff=False)
            menubar.add_cascade(label = elem, underline = 0, menu = menuBar[elem]) 

        menuOpt = []
#         menuOpt.append(('command', 'Open','Ctrl+O', 0, self.__openFile))        
        menuOpt.append(('command', 'Save','Ctrl+S', 0, self.saveFile))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Import File','Ctrl+M', 0, self.importFile))
        menuOpt.append(('command', 'Export File','Ctrl+E', 0, self.exportFile))
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Remove Folder','', 0, self.removeModule))
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Print','Ctrl+P', 0, self.dummyCommand))
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Close','Alt+Q', 0, sys.exit))
        self.makeMenu('File', menuOpt)
        
        menuOpt = []
        menuOpt.append(('command', 'Undo','Ctrl+Z', 0, self.dummyCommand))
        menuOpt.append(('command', 'Redo','', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Cut','Ctrl+X', 0, self.pyEditor.selCut))
        menuOpt.append(('command', 'Copy','Ctrl+C', 0, self.pyEditor.selCopy))
        menuOpt.append(('command', 'Paste','Ctrl+V', 0, self.pyEditor.selPaste))
        menuOpt.append(('command', 'Clear','Del', 0, self.pyEditor.selDel))
        menuOpt.append(('command', 'Select All','Ctrl+A', 0, self.pyEditor.selAll))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Find','Ctrl+F', 0, self.dummyCommand))
        menuOpt.append(('command', 'Find Next','F3', 0, self.dummyCommand))
        menuOpt.append(('command', 'Replace','Ctrl+H', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Indent','Tab', 0, self.dummyCommand))
        menuOpt.append(('command', 'Outdent','Shift+Tab', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('cascade', 'Bookmarks', 0))
        self.makeMenu('Edit', menuOpt)        

        menuOpt = []
        menuOpt.append(('command', 'Toogle Bookmark','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Next Bookmark','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Previous Bookmark','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Clear All Bookmark','', 0, self.dummyCommand))        
        self.makeMenu('Edit.Bookmarks', menuOpt)
        
        menuOpt = []
        menuOpt.append(('command', 'Code','F7', 0, self.dummyCommand))
        menuOpt.append(('command', 'Object','Shift+F7', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Definition','Shift+F2', 0, self.dummyCommand))
        menuOpt.append(('command', 'Last Position','Ctrl+Shift+F2', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Object Browser','Ctrl+G', 0, self.dummyCommand))
        menuOpt.append(('command', 'Locals Window','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Watch Window','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Call Stack','', 0, self.dummyCommand))
        self.makeMenu('View', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'listFolder','', 0, self.insertListFolder))
        menuOpt.append(('command', 'ParseFolder','', 0, self.insertParseFolder))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'MediaAddress','', 0, self.insertMediaAddress))        
        self.makeMenu('Insert', menuOpt)
        
        menuOpt = []
        menuOpt.append(('command', 'Run Macro','F5', 0, self.onRun))
        menuOpt.append(('command', 'Break','Ctrl+Break', 0, self.dummyCommand))
        menuOpt.append(('command', 'Reset','', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Design Mode','', 0, self.dummyCommand))        
        self.makeMenu('Run', menuOpt)


    def menuConf(self):
        menuState = lambda equis: tk.NORMAL if equis else tk.DISABLED
        moduleId = self.getTreeModuleSel(self.actTreeSel)
        modName = 'Remove ' + moduleId.rpartition('.')[2]
        menuFile = self.menuBar['File']
        menuFile.entryconfigure(5, label = str(modName))
        editOp = menuState(self.treeview.set(moduleId, column = 'iType') == 'mod' and moduleId.rpartition('.')[2] != 'initScripts')
        menuFile.entryconfigure(5, state = editOp)

        menuEdit = self.menuBar['Edit']
        editOp = menuState(self.pyEditor.textw.tag_ranges('sel'))
        for ene in [3, 4, 6]:     # cut, copy, clear
            menuEdit.entryconfigure(ene, state = editOp)
        
#         menuInsert = self.menuBar['Insert']
#         moduleId = self.treeview.focus()
#         iType = self.treeview.set(moduleId, column ='iType')
#         editOp = menuState(iType == 'folder')
#         for ene in [0, 1, 3]:     
#             menuInsert.entryconfigure(ene, state = editOp)
         


    def registerNode(self, treeview, iid, childName = False):
        if treeview.exists(iid): return
        iidPart = iid.rpartition('.')
        if len(iidPart[1]) and not treeview.exists(iidPart[0]):
            self.registerNode(treeview, iidPart[0], childName)
        treeview.insert(iidPart[0], 'end',iid)
        if childName:
            treeview.item(iid, text = iidPart[2])

    def getTextTree(self, text, prefix = ''):    
        prefixID = ''
        fileTree = []
        tIter = re.finditer('^([ \t]*)(def|class)[ \t]+([^\(:)]*).*:', text, re.MULTILINE)
        for match in tIter:
            indent = (match.end(1) - match.start(1))/4 if match.group(1) else 0
            while prefixID.count('.') and indent <= prefixID.count('.')-1:
                prefixID = prefixID.rpartition('.')[0]
            prefixID = prefixID + '.' + match.group(2) + '('+match.group(3)+')'
            prefixMOD = prefix + prefixID if prefix else prefixID[1:]
            fileTree.append((prefixMOD, match.group(3), match.start(3), match.end(3)))
        return fileTree
            
    def fetchTextOutline(self,text, moduleID):
        fileTree = self.getTextTree(text, prefix = moduleID)
        for child in fileTree:
            self.registerNode(self.treeview, child[0], child[1])
            self.treeview.set(child[0],column = 'iType', value = 'pos')
            self.treeview.set(child[0],column = 'info', value = (child[2],child[3]))
        
    def __openFile(self):
        try:
            with open('treeViewDump','rb') as f:
                leaves = pickle.load(f)
        except IOError:
            leaves = ['rootmenu.opcion1']
            leaves.append(['rootmenu', dict(iType ='listFolder')])
            leaves.append(['rootmenu.opc1', dict(name = 'Ultimos Capitulos', iType ='parseFolder', command ="episodios", params='1.0')])
            leaves.append(['rootmenu.opc1.opc1', dict(iType ='parseFolder', command ="mediaParser", params='1.0')])
            leaves.append(['rootmenu.opc2', dict(name = 'Ultimas Series Agregadas',iType ='parseFolder', command ='series', params='1.0')])
            leaves.append(['rootmenu.opc2.opc1', dict(iType ='parseFolder', command ="mediaParser", params='1.0')])
            
            leaves.append(['rootmenu.opc3', dict(name = 'Genero',iType ='parseFolder', command ='print("tercero")', params='1.0')])
            leaves.append(['rootmenu.opc4', dict(name = 'A-Z',iType ='parseFolder', command ='print("tercero")', params='1.0')])
            leaves.append(['rootmenu.opc5', dict(name = 'Buscar',iType ='parseFolder', command ='print("tercero")', params='1.0')])
        
        for elem in leaves[1:]:
            self.registerNode(self.treeview, elem[0], childName = True)
            for dKey, dValue in elem[1].items():
                self.treeview.set(elem[0], column = dKey, value = dValue)
            if elem[1]['iType'] == 'mod':
                text = elem[1]['info']
                self.fetchTextOutline(text, elem[0])
        
        selItem = leaves[0]
        while selItem.rpartition('.')[1]:
            self.treeview.item(selItem.rpartition('.')[0], open = True )
            selItem = selItem.rpartition('.')[0]
        self.treeview.selection_set(leaves[0])
        self.treeview.focus(leaves[0])
        self.setTreeModuleSel(leaves[0], saveFlag = False)
        self.pyEditor.onUpRelease()            
        self.pyEditor.textw.see('insert')
        self.pyEditor.textw.focus_force()
        
    def saveFile(self):
        def getLeavesOf(treeview, iid):
            if iid != '':
                colValues = treeview.set(iid)            
                leaves = [(iid, colValues)]
                if colValues['iType'] == 'mod':
                    return leaves
            else:
                leaves = []                
            for child in treeview.get_children(iid):
                childLeaves = getLeavesOf(treeview, child)
                leaves.extend(childLeaves)
            return leaves

        moduleID = self.getTreeModuleSel(self.actTreeSel)
        self.setTreeModuleSel(moduleID, saveFlag = True)
        leaves = getLeavesOf(self.treeview,'')
        leaves.insert(0,self.actTreeSel)
        with open('treeViewDump','wb') as f:
            pickle.dump(leaves, f)
        
    def importFile(self):
        name = tkFileDialog.askopenfilename(filetypes=[('Python Scripts', '*.py'),('Text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            with open(name, 'r', encoding='utf_8') as f:
                data = f.read()
            self.insertText(data)
        
    def exportFile(self):
        name = tkFileDialog.asksaveasfilename(filetypes=[('Python Scripts', '*.py'),('Text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            data = self.pyEditor.getContent()
            with open(name, 'w', encoding = 'utf_8') as f:
                f.write(data)      
                
    def removeModule(self):
        moduleId = self.getTreeModuleSel(self.actTreeSel)
        moduleName = moduleId.rpartition('.')[2]
        title = 'WARNING'
        message = 'Do you want to export ' + moduleName + 'before removing it?'
        userAns = tkMessageBox.askquestion(title, message, default=tkMessageBox.YES) 
        if userAns == tkMessageBox.YES:
            self.exportFile()
        leaves = 'rootmenu'
        self.treeview.selection_set(leaves)
        self.treeview.focus(leaves)
        self.setTreeModuleSel(leaves, saveFlag = False)
        self.pyEditor.onUpRelease()            
        self.pyEditor.textw.see('insert')
        self.pyEditor.textw.focus_force()
        self.treeview.delete(moduleId)
        
    def insertElement(self, elemType, strType, parentId):
        elemName = tkSimpleDialog.askstring('Insert ' + strType, 'Nombre del ' + strType + ' a incluir:')
        childId = parentId + '.' + elemName
        self.treeview.insert(parentId, 'end', childId, text = elemName)
        self.treeview.set(childId, column = 'iType', value = elemType)
        return childId
        
    def insertListFolder(self, folderName = None):
        parentId = self.treeview.focus()
        if not folderName:
            folderName = tkSimpleDialog.askstring('Insert nuevo elemento', 'Nombre del nuevo elemento a incluir:')
            if not folderName: return
        childId = parentId + '.' + folderName 
        self.registerNode(self.treeview, childId, childName = True)
        self.treeview.set(childId, column = 'iType', value = 'listfolder')
        self.treeview.item(parentId, open = True )  
        self.treeview.selection_set(childId)
        self.treeview.focus(childId)
        return childId
        
    def insertParseFolder(self, folderName = None, name = '', regexp = ''):
        parentId = self.treeview.focus()
        if not folderName:
            folderName = tkSimpleDialog.askstring('Insert nuevo elemento', 'Nombre del nuevo elemento a incluir:')
            if not folderName: return
        if self.parseThreads.get(folderName, None):
            pass
        else:
            parseThreads = self.parseThreads[folderName]
            parseThreads['name'] = name
            parseThreads['numInComingThreads'] = parseThreads.get('numInComingThreads',0) + 1
            parseThreads['regexp'] = regexp
            parseThreads['nxtThread'] = None
            
            childId = parentId + '.' + folderName 
            self.registerNode(self.treeview, childId, childName = True)
            self.treeview.set(childId, column = 'iType', value = 'Parsefolder')
            self.treeview.item(parentId, open = True )  
            self.treeview.selection_set(childId)
            self.treeview.focus(childId)
        return childId

        
    def insertModule(self, modName = None):
        moduleId = self.insertFolder(modName)
        for dKey, dValue in dict(iType = 'mod', info = '#      modulo insertado', insPos = '1.0').items():
            self.treeview.set(moduleId, column = dKey, value = dValue)
        self.setTreeModuleSel(moduleId, saveFlag = True)
        return moduleId

    def insertText(self, data):
        moduleID = self.getTreeModuleSel(self.actTreeSel)
        moduleChild = self.treeview.get_children(moduleID)
        self.treeview.delete(*moduleChild)
        textHead = self.pyEditor.textw.get('1.0', 'insert')
        textTail = self.pyEditor.textw.get('insert', 'end')
        data = textHead + data + textTail
        self.pyEditor.setContent(data)
        self.fetchTextOutline(data, moduleID)
        insPos = self.treeview.set(moduleID, column = 'insPos')
        self.pyEditor.textw.mark_set('insert', insPos)
        

    def insertMediaAddress(self):
        name = tkFileDialog.askopenfilename(filetypes=[('Python Scripts', '*.py'),('Text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            modName = os.path.basename(name)
            modName = os.path.splitext(modName)[0]
            self.insertModule(modName)
            with open(name, 'r', encoding='utf_8') as f:
                data = f.read()
            self.insertText(data)
            self.pyEditor.onUpRelease()            
            self.pyEditor.textw.see('insert')
            self.pyEditor.textw.focus_force()

        
    def onRun(self):
        text = self.pyEditor.getContent()
        self.runScript(text)
        
    def runScript(self,text):
        self.pyConsole.textw.insert('end', 'Running editor content:\n' )
        self.pyConsole.runPythonExpr(text)
        self.pyConsole.dispPrompt()
        self.pyConsole.textw.see('end')
        
            
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
        
    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')

    def popUpMenu(self):
        popup = tk.Menu(self, tearoff = 0)
        popup.add_command(label = 'Next')
        popup.add_command(label = 'Previous')
        popup.add_separator()
        popup.add_command(label = 'Home')
        self.popup = popup
    
    def do_popup(self, event):
        try:
            self.popup.tk_popup(event.x_root, event.y_root,0)
        finally:
            self.popup.grab_release()
        
    def getTreeModuleSel(self, codeID):
        if codeID:
            while True:
                selType = self.treeview.set(codeID,column= 'iType')
                if selType  == 'mod': break
                codeID = codeID.rpartition('.')[0]
            if selType != 'mod': codeID = None
        return codeID
            
    def setTreeModuleSel(self, codeID, saveFlag = True):
        moduleID = self.getTreeModuleSel(codeID)
        if moduleID:
            actTreeModule = self.getTreeModuleSel(self.actTreeSel)
            if saveFlag and actTreeModule: 
                text = self.pyEditor.getContent()
                insertIndx = self.pyEditor.textw.index('insert')
                self.treeview.set(actTreeModule,column ='info', value = text)
                self.treeview.set(actTreeModule,column ='insPos', value = insertIndx)
            if moduleID != actTreeModule: 
                text = self.treeview.set(moduleID,column = 'info')
                insertIndx = self.treeview.set(moduleID,column = 'insPos')
                self.pyEditor.setContent(text)
                self.pyEditor.textw.mark_set('insert', insertIndx)
        self.actTreeSel = moduleID


        
    def onTreeSelection(self, event = None):
        codeID = self.treeview.focus()
        if(self.treeview.set(codeID, column = 'iType') == 'folder'): return
        self.setTreeModuleSel(codeID)
        if self.treeview.set(codeID, column = 'iType') == 'pos':
            selLim = self.treeview.set(codeID, column = 'info')
            frstPos = '1.0 + %d chars'% selLim[0]
            scndPos = '1.0 + %d chars'% selLim[1]
            self.pyEditor.textw.tag_remove('sel', '1.0', 'end')
            self.pyEditor.textw.tag_add('sel', frstPos, scndPos)
            self.pyEditor.textw.mark_set('insert', scndPos)
            self.pyEditor.onUpPress()
        self.pyEditor.textw.see('insert')            
        self.pyEditor.onUpRelease()            
        self.pyEditor.textw.focus_force()
    
    def scriptTree(self, parent):
        self.popUpMenu()        
        treeview = ttk.Treeview(parent, show = 'tree', columns = ('name', 'iType','command', 'params'), displaycolumns = ())
        treeview.pack(fill = tk.BOTH, expand = tk.YES)
        treeview.event_add('<<myEvent>>','<Double-1>','<Return>')
        treeview.bind('<<myEvent>>', self.onTreeSelection)
        treeview.bind('<Button-3>',self.do_popup)
        self.treeview = treeview
        self.actTreeSel = None
        self.__openFile()
        return
    
    def setGUIControls(self):
        self.setCustomFont()
        frame1 = tk.Frame(self)
        frame1.pack(fill = tk.X)
        label = tk.Label(frame1, text = "Instruction:")
        label.pack(side = tk.LEFT)
        self.strPythonInst = tk.StringVar()
        entry = tk.Entry(frame1, textvariable = self.strPythonInst, font = self.customFont)
        entry.pack(side=tk.LEFT, fill = tk.X, expand = 1 )
        entry.bind('<Key>', self.keyHandler)
        button = tk.Button(frame1, text = "Run", command = self.runPythonInst)
        button.pack(side = tk.RIGHT)

        
    def Close(self):
        self.destroy()
        

if __name__ == "__main__":
    Root = tk.Tk()
#     Root.option_add('*tearOff', False)
    Root.withdraw()
    xbmcMenu()
    Root.mainloop()
