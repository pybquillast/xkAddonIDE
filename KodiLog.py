'''
Created on 5/05/2015

@author: Alex Montes Barrios
'''
import Tkinter as tk
import Queue
import keyword
import tkFont
import ttk
import tkMessageBox
import HTMLParser
import urllib
import re
import CustomRegEx
import os
import SintaxEditor

class kodiLog(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.stopFlag = False
        self.activeCallBack = []        
        self.queue = Queue.Queue(maxsize=0)
        self.fileListProv = None
        self.isCoderSet = False
        self.bind("<FocusIn>", self.widget_got_focus)
        self.setIdeServerAddress(('localhost', 5000))
        self.setGUI()

    def setIdeServerAddress(self, serveraddress):
        self.serveradress = serveraddress

    def getIdeServerAddress(self):
        return self.serveradress

    def widget_got_focus(self, *args, **kwargs):
        if self.sntxIndx.get() == 1:
            self.getKodiLog(refreshFlag=True)
        
    def setFileListProv(self, callBackFunction):
        self.fileListProv = callBackFunction
        
    def initFrameExec(self, coder, param = False):
        if param or not self.isCoderSet:
            self.coder = coder
            self.isCoderSet = True
            self.fillDropDownLst()
            self.fileChsr.current(0)
            self.sntxIndx.set(0)
        activeKnotId = self.coder.getActiveNode()
        srchStr = 'def ' + activeKnotId + '():'
        srchIndx = self.textw.search(srchStr, '1.0')
        if srchIndx:
            self.textw.mark_set('insert', srchIndx) 
            self.textw.see('insert')
            self.onUpRelease()
            self.textw.focus_set()
            
    def setGUI(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        topPane = tk.Frame(self)
        topPane.pack(side = tk.TOP, fill = tk.X)
        self.sntxIndx = intVar = tk.IntVar()
        intVar.trace('w', self.changeDisplay)
        for k, elem in enumerate(['IDE.log', 'Kodi.log', 'pastebin.com']):
            boton = tk.Radiobutton(topPane, text = elem, width = 30, value = k, variable = intVar, indicatoron = 0)
            boton.pack(side = tk.LEFT)

        self.xbmclogComId = tk.StringVar()
        self.RightTopPane = RightTopPane = tk.Frame(topPane)
        RightTopPane.pack(side=tk.RIGHT)
        tk.Button(RightTopPane, text = 'Get', command = self.getUrlLog).pack(side = tk.RIGHT)
        tk.Entry(RightTopPane, textvariable = self.xbmclogComId).pack(side = tk.RIGHT)
        tk.Label(RightTopPane, text = 'http://pastebin.com/: ').pack(side = tk.RIGHT)

        self.sintaxEd = SintaxEditor.SintaxEditor(self)
        self.sintaxEd.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        self.setHyperlinkManager(self.click_hyperlink)
        self.sntxIndx.set(1)
        
    def setHyperlinkManager(self, hyperLinkManager):
        self.sintaxEd.setHyperlinkManager(hyperLinkManager)

    def getLogContent(self, logUrl):
        f = urllib.urlopen(logUrl)
        content = f.read().decode('utf-8')
        f.close()
        return content

    def getIdeLog(self):
        logUrl = 'http://%s:%s/file://log' % self.getIdeServerAddress()
        content = self.getLogContent(logUrl)
        contentDesc = (content, 'filegen', logUrl)
        sintaxArray = self.errorSintax()
        self.sintaxEd.setContent(contentDesc,'1.0', sintaxArray, isEditable = False)

    def getUrlLog(self):
        if self.sntxIndx.get() != 2: return
        logId = self.xbmclogComId.get()
        if logId:
            logUrl = 'http://pastebin.com/' + logId
            content = self.getLogContent(logUrl)
            parser = HTMLParser.HTMLParser()
            pattern = r'(?#<li class="li[0-9]" div.*=linea>)'
            lines = map(parser.unescape, CustomRegEx.findall(pattern, content))
            content = '\n'.join(lines)          #.replace('&nbsp;', '')
        else:
            logUrl, content = '', ''
        contentDesc = (content, 'filegen', logUrl)
        sintaxArray = self.errorSintax()
        self.sintaxEd.setContent(contentDesc,'1.0', sintaxArray, isEditable = False)
        
    
    def click_hyperlink(self, texto):
        tkMessageBox.showinfo('Hyperlink', texto)        
        return       
        
    def fillDropDownLst(self):
        dropDownContent = []
        if self.fileListProv:
            lista =  self.fileListProv()
            self.listaPy = [pFile for pFile in lista if pFile[0].endswith('.py')]
            dropDownContent = map(os.path.basename, [elem[0] for elem in self.listaPy])
        self.fileChsr.configure(values = dropDownContent)
        
    def errorSintax(self):
        toColor = [
                   ['errError', dict(background = 'red'), r'ERROR:',re.MULTILINE],
                   ['errWarning', dict(background = 'yellow'), r'WARNING:',re.MULTILINE],
                   ['hyper', dict(foreground="blue", underline=1), r'File "[^<][^"]+", line [0-9]+, in [\w<>]+',re.MULTILINE],
                   ['hyper', dict(foreground="blue", underline=1), r'http:[^\n|]+',0]
                   ]
        return toColor
        
    def getKodiLog(self, refreshFlag=False):
        from xbmc import translatePath
        key = self.sintaxEd.getContent()[2]
        logfile = os.path.join(translatePath('special://logpath'), 'kodi.log')
        modtime = os.path.getmtime(logfile)
        newkey = '%s_%s' % (logfile, modtime)

        if refreshFlag and key != newkey:
            answ = tkMessageBox.askyesno('Kodi.log modified', 'The kodi.log file has being modified.\nDo you want to refresh the content?')
            if not answ: return

        if key != newkey:
            with open(logfile, 'r') as f:
                content = f.read()
            contentDesc = (content, 'file', newkey)
            sintaxArray = self.errorSintax()
            self.sintaxEd.setContent(contentDesc,'1.0', sintaxArray, isEditable = False)

    def changeDisplay(self, *args, **kwargs):
        if  self.sntxIndx.get() == 0:
            self.RightTopPane.pack_forget()
            self.getIdeLog()
        elif self.sntxIndx.get() == 1:
            self.RightTopPane.pack_forget()
            self.getKodiLog()
        elif self.sntxIndx.get() == 2:
            self.RightTopPane.pack(side=tk.RIGHT)
            self.getUrlLog()
            
        

        
    
if __name__ == '__main__':
    Root = tk.Tk()
    kodilog = kodiLog(Root)
    kodilog.pack(side =tk.TOP, fill = tk.BOTH, expand = tk.YES) 
    Root.mainloop()
    
         
