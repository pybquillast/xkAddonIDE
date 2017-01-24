# -*- coding: utf-8 -*-
'''
Created on 27/06/2014

@author: Alex Montes Barrios
'''
import os
import Tkinter as tk
import tkSimpleDialog
import tkMessageBox

import idewidgets
import menuThreads
import thread
import ttk
import tkFont
import urllib
import collapsingFrame
import KodiLog
import SintaxEditor
import urlparse
import re
import CustomRegEx
import network
import Queue
import xml.etree.ElementTree as ET
from OptionsWnd import scrolledFrame, AppSettingDialog
import threading
import imageProcessor as imgp

"a simple customizable scrolled listbox component"

import tkFileDialog

class RegexpBar(tk.Frame):
    def __init__(self, master, messageVar):
        tk.Frame.__init__(self, master)
        self.dropDownFiler = None
        self.textWidget = None
        self.actMatchIndx = 0

        self.mutex = threading.Event()
        self.queue = Queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'
        
        self.messageVar = messageVar
        self.setGUI()

    def setTextWidget(self, tWidget):
        self.textWidget = tWidget
        
    def setTreeWidget(self, treeWdgt):
        self.tree = treeWdgt
        self.tree.bind('<<TreeviewSelect>>', self.onTreeSel)

    def onTreeSel(self,event):
        treew = event.widget
        selId = treew.selection()[0]
        posINI = treew.set(selId, column = 'posINI')
        posFIN = treew.set(selId, column = 'posFIN')
        self.setActualMatch((posINI, posFIN))

    def setDropDownFiler(self, callbckFunc):
        self.dropDownFiler = callbckFunc
        
    def setGUI(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        
        frame1 = tk.Frame(self)
        frame1.pack(fill = tk.X)

        iconImage = imgp.getFontAwesomeIcon
        commOptions = dict(size=24,isPhotoImage=True, color='black', aspectratio='stretch')

        self.lstIcon = lstIcon = iconImage('fa-angle-double-right', **commOptions)
        self.frstIcon = frstIcon = iconImage('fa-angle-double-left', **commOptions)
        self.nxtIcon = nxtIcon = iconImage('fa-angle-right', **commOptions)
        self.prvIcon = prvIcon = iconImage('fa-angle-left', **commOptions)
        self.anchorIcon = anchorIcon = iconImage('fa-anchor', **commOptions)

        self.anchor = tk.IntVar()
        self.anchorPos = []

        navFrame = tk.Frame(frame1)
        navFrame.pack(side=tk.RIGHT)
        self.leftWing = leftWing = tk.Frame(navFrame)
        leftWing.pack(side=tk.LEFT)
        self.rightWing = rightWing = tk.Frame(navFrame)
        rightWing.pack(side=tk.RIGHT)

        self.butLast = tk.Button(rightWing, image=lstIcon, font = self.customFont, text = "L", command = lambda: self.extreme('>>'))
        self.butLast.pack(side = tk.RIGHT)
        self.butNext = tk.Button(rightWing, image=nxtIcon, font = self.customFont, text = ">", command = self.nextMatch)
        self.butNext.pack(side = tk.RIGHT)
        self.matchLabel = tk.Label(navFrame, font = self.customFont, text = "")
        self.matchLabel.pack(side = tk.LEFT)
        self.butPrev = tk.Button(leftWing, image=prvIcon, font = self.customFont, text = "<", command = self.prevMatch)
        self.butPrev.pack(side = tk.RIGHT)
        self.butFirst = tk.Button(leftWing, image=frstIcon, font = self.customFont, text = "F", command = lambda: self.extreme('<<'))
        self.butFirst.pack(side = tk.RIGHT)

        self.butAnchor = tk.Checkbutton(frame1, image=anchorIcon, variable=self.anchor, indicatoron=0, font = self.customFont, text = "A", command = self.onAnchor)
        self.butAnchor.pack(side = tk.LEFT, fill=tk.Y)
        self.butKeyMaker = tk.Button(frame1, text = "ZoomIn", command = self.zoomInOut)
        self.butKeyMaker.pack(side = tk.LEFT, padx=4, fill=tk.Y)
        self.cbIndex = tk.StringVar()
        tk.Label(frame1, textvariable = self.cbIndex).pack(side = tk.LEFT)
        self.regexPattern = tk.StringVar()
        cbStyle = ttk.Style()
        cbStyle = cbStyle.configure('red.TCombobox', foreground='red')
        self.entry = ttk.Combobox(frame1,
                                  font = self.customFont,
                                  textvariable = self.regexPattern)
        self.entry.configure(postcommand = self.fillDropDownLst)
        self.entry.pack(side=tk.LEFT, fill = tk.X, expand = 1 )

        self.entry.event_add('<<re_escape>>','<Control-E>','<Control-e>')
        self.entry.bind('<<re_escape>>', self.selPasteWithReEscape)
        self.entry.bind('<Return>', lambda event: self.extreme('<<'))
        self.entry.bind('<FocusIn>', self.onFocusEvent)
        self.entry.bind('<FocusOut>', self.onFocusEvent)
        self.entry.bind('<<ComboboxSelected>>', self.getPatternMatch)


        frame15 = tk.Frame(self)
        frame15.pack(fill = tk.X)
        label = tk.Label(frame15, text = "Compilation Flags:", font = self.customFont)
        label.pack(side = tk.LEFT)

        self.chkVar = {}
        chkTxt = CustomRegEx.FLAGS
        for elem in chkTxt:
            self.chkVar[elem] = tk.IntVar()
            chkbutt = tk.Checkbutton(frame15, text = elem, variable = self.chkVar[elem], font = self.customFont)
            chkbutt.bind('<Button-1>', self.flagToggle)
            chkbutt.pack(side = tk.LEFT)

        frame3 = tk.Frame(self)
        cmbbxValues = ['[^X]+', '.+?', r'\w+', r'\W+?', r'(?P=<keyName>)']
        self.cmbbxPattern = ttk.Combobox(frame3, font = self.customFont, values = cmbbxValues)
        self.cmbbxPattern.pack(side=tk.LEFT, fill = tk.X )
        cmbbxIntVar = tk.IntVar()
        self.cmbbxIntVar = cmbbxIntVar
        for k, elem in enumerate(['Pattern', 'Key']):
            boton = tk.Radiobutton(frame3, text = elem, width = 15, value = k, variable = cmbbxIntVar)
            boton.pack(side = tk.LEFT)

        cmbbxValues = ['url', 'label', 'iconImage', 'thumbnailImage', 'SPAN', 'SEARCH', 'NXTPOSINI']
        self.cmbbxKey = ttk.Combobox(frame3, font = self.customFont, values = cmbbxValues)
        self.cmbbxKey.pack(side=tk.LEFT, fill = tk.X )

        boton = tk.Button(frame3, font = self.customFont, text = "Apply", command = self.keyMaker)
        boton.pack(side = tk.LEFT)

    def onFocusEvent(self, event):
        if event.type == '9':
            self.wtracer = self.regexPattern.trace("w", self.getPatternMatch)
        elif event.type == '10':
            self.regexPattern.trace_vdelete("w", self.wtracer)

    def onAnchor(self):
        textw = self.textWidget
        if self.anchor.get() == 1:
            height = textw.winfo_height()
            wndINI = textw.index('@0,0')
            wndFIN = textw.index('@0,%s' % height)
            seeIndx = textw.index('@0,%s' % (height/2))
            self.anchorPos = [(wndINI, wndFIN, seeIndx)]
        else:
            wndINI, wndFIN, seeIndx = self.anchorPos.pop()
            textw.see(seeIndx)

    def setZoomManager(self, callBackFunc):
        self.zoomManager = callBackFunc

    def setZoomType(self, zoomType):
        self.butKeyMaker.config(text = zoomType)

    def getZoomType(self):
        return self.butKeyMaker.cget('text')

    def zoomInOut(self):
        if self.zoomManager:
            btnText = self.butKeyMaker.cget('text')
            retValue = self.zoomManager(btnText)
            if retValue:
                indx = 1 - ['ZoomIn', 'ZoomOut'].index(btnText)
                self.setZoomType(['ZoomIn', 'ZoomOut'][indx])

    def selPasteWithReEscape(self, event = None):
        textw = self.entry
        text = textw.selection_get(selection = 'CLIPBOARD')
        try:
            if text:
                if textw.select_present():
                    textw.delete('sel.first', 'sel.last')
                text = ''.join([(re.escape(elem) if elem in '()?.*{}[]+\\' else elem) for elem in text])
                textw.insert('insert', text)
        except tk.TclError:
            pass
        return 'break'


    def fillDropDownLst(self):
        if not self.dropDownFiler: return
        self.theValues = self.dropDownFiler()
        cbValues = [val[0]+val[1] for val in self.theValues if val[1]]
        self.entry.configure(values = cbValues)

    def extreme(self, widgetText):
        if widgetText == '<<':
            npos = 0
        elif widgetText == '>>':
            npos = -1
        children = self.tree.get_children()
        iid = children[npos]
        self.tree.selection_set(iid)

    def keyMaker(self):
        tagName = self.cmbbxKey.get()
        tagPattern = self.cmbbxPattern.get()
        entryTxt = self.regexPattern.get()
        if tagName in ['SPAN', 'NXTPOSINI']:
            entryTxt = '(?#<' + tagName +'>)' + entryTxt
        elif self.entry.select_present():
            selText = self.entry.selection_get()
            posIni = entryTxt.find(selText)
            posFin = posIni + len(selText)
            if tagPattern == '[^X]+': tagPattern = tagPattern.replace('^X', '^' + entryTxt[posFin])
            if tagPattern == r'(?P=<keyName>)': tagReplace = tagPattern.replace('<keyName>', tagName)
            elif tagName == 'SEARCH':
                entryTxt = '(?#<SEARCH>)' + entryTxt
                tagReplace = '<search>'
                posIni += len('(?#<SEARCH>)')
                posFin += len('(?#<SEARCH>)')
            elif self.cmbbxIntVar.get() == 1:
                tagReplace = '(?P<' + tagName +'>' + tagPattern + ')'
            elif self.cmbbxIntVar.get() == 0:
                tagReplace = tagPattern
            entryTxt = entryTxt[:posIni] + tagReplace + entryTxt[posFin:]
            posFin = posIni + len(tagReplace)
            self.entry.select_range(posIni, posFin)
            self.entry.icursor(posFin)
        self.regexPattern.set(entryTxt)


    def actMatch(self, nPos):
        selTag = 'I{:03x}'.format(nPos)
        # selTag = selTag.upper()
        self.tree.see(selTag)

    def getRegexpPattern(self, withFlags=False):
        regExPat = self.regexPattern.get()
        if withFlags:
            regExPat = self.getCompFlagsPatt() + regExPat
        return regExPat

    def getCompFlags(self):
        compflags = ['re.' + key for key in CustomRegEx.FLAGS if self.chkVar[key].get()]
        return '|'.join(compflags) if compflags else '0'

    def getCompFlagsPatt(self):
        compFlags = self.getCompFlags()
        return CustomRegEx.getCompFlagsPatt(compFlags)

    def setCompFlagsPatt(self, comFlagsPatt):
        comFlagsPatt = CustomRegEx.getCompFlags(comFlagsPatt)
        comFlags = '|'.join(map(lambda x: 're.%s' % x, comFlagsPatt))
        self.setCompFlags(comFlags)

    def setCompFlags(self, compflags):
        if compflags == -1: compflags = ''
        keyFlags = compflags.replace('re.', '').split('|') if compflags else []
        for key in self.chkVar.keys():
            flag = True if key in keyFlags else False
            self.chkVar[key].set(flag)

    def setRegexpPattern(self, regexp):
        if regexp:
            rgxflags, crgflags, regexp = CustomRegEx.getFlagsRegexPair(regexp)
            compFlags = rgxflags + crgflags
            if compFlags:
                self.setCompFlagsPatt(compFlags)
        self.regexPattern.set(regexp)

    def setActualMatch(self, selTag):
        textw = self.textWidget
        selTag = map(lambda x: textw.index('1.0  + %s chars'% x), selTag)
        index = selTag[0]
        while True:
            index = textw.mark_next(index)
            if index.startswith('I'): break

        assert textw.index(index) == selTag[0]
        nPos = int(index[1:], 16)           # Para corregir verificar que la marca es Ixxx

        matchStr = self.matchLabel.cget('text')
        n = matchStr.find(' de ')
        matchStr = ' '  + str(nPos) + matchStr[n:]
        self.actMatchIndx = nPos

        self.textWidget.tag_remove('actMatch', '1.0', 'end')
        self.textWidget.tag_add('actMatch', *selTag)
        self.textWidget.mark_set('insert', selTag[0])

        dif = len(self.textWidget.get(*selTag))
        line, col = str(selTag[0]).split('.')
        self.messageVar.set('Ln: %s Col: %s Sel:%s' % (line, col, dif))

        self.textWidget.see(selTag[1])
        self.textWidget.see(selTag[0])
        self.matchLabel.config(text=matchStr, bg = 'SystemButtonFace')

        self.actMatch(nPos)

    def getBorderTags(self, indexPos):
        textw = self.textWidget
        def getNextItem(indexPos):
            index = indexPos = textw.index(indexPos)
            while True:
                index = textw.mark_next(index)
                if index:
                    if index.startswith('I') and textw.index(index) != indexPos:
                        break
                else:
                    index = '1.0'
            return index

        def getPreviousItem(indexPos):
            index = indexPos = textw.index(indexPos)
            while True:
                index = textw.mark_previous(index)
                if index:
                    if index.startswith('I') and textw.index(index) != indexPos:
                        break
                else:
                    index = tk.END
            return index

        nxtMark = getNextItem(indexPos)
        prevMark = getPreviousItem(indexPos)

        if 'actMatch' in textw.tag_names(indexPos) and 'actMatch' in textw.tag_names(prevMark):
            prevMark = getPreviousItem(prevMark)

        return (prevMark, nxtMark)

    def nextMatch(self):
        insPoint = self.textWidget.index(tk.INSERT)
        iid = self.getBorderTags(insPoint)[1]
        # iid = 'I{:03x}'.format(iid).upper()
        self.tree.selection_set(iid)

    def prevMatch(self):
        insPoint = self.textWidget.index(tk.INSERT)
        iid = self.getBorderTags(insPoint)[0]
        # iid = 'I{:03x}'.format(iid).upper()
        self.tree.selection_set(iid)


    def flagToggle(self, event):
        widget = event.widget
        widget.toggle()
        self.getPatternMatch()
        return 'break'

    def getPatternMatch(self, *dummy):
        pattern = self.regexPattern.get()
        if self.entry.current() != -1 and self.entry.get() == pattern:
            ndx, pattern = re.match(r'(?P<ndx>\(\?#<r.+?>\))?(?P<rgx>.+?)\Z', pattern).groups()
            self.cbIndex.set(ndx)
        else:
            if self.cbIndex.get():
                cbValues = self.entry.cget('values')
                if self.cbIndex.get() + pattern not in cbValues: self.cbIndex.set('')
        self.setRegexpPattern(pattern)
        self.formatContent()
        if self.cbIndex.get():
            self.textWidget.focus_force()
        pass

    def formatContent(self, index1 = '1.0', index2 = 'end'):
        mutex = self.mutex
        if self.activeCallBack:
            idAfter = self.activeCallBack.pop()
            self.after_cancel(idAfter)
        if mutex.is_set():
            mutex.clear()
            if self.t.isAlive():
                self.t.join(10)
                mutex.clear()

        self.queue.queue.clear()
        self.removeTags('1.0', 'end')

        regexPattern = self.getRegexpPattern()
        if not regexPattern: return None
        regexPattern = self.getRegexpPattern(withFlags=True)
        rgxflags, crgflags, regexPattern = CustomRegEx.getFlagsRegexPair(regexPattern)
        regexPattern = crgflags + regexPattern
        compileOp = CustomRegEx.getCompFlags(rgxflags)
        matchLabel = self.matchLabel

        opFlag = {'UNICODE':re.UNICODE, 'DOTALL':re.DOTALL, 'IGNORECASE':re.IGNORECASE,
                  'LOCALE':re.LOCALE, 'MULTILINE':re.MULTILINE, 'VERBOSE':re.VERBOSE}
        compFlags = reduce(lambda x,y: x|y,[opFlag[key] for key in compileOp],0)

        content = self.textWidget.get(index1, index2)
        if not content.strip(' \n\r\t\f'): return None
        baseIndex = self.textWidget.index(index1)


        yesCompFlag = len(regexPattern) > 0
        if not yesCompFlag:
            matchLabel.config(text = '', bg = 'SystemButtonFace')
            return None
        self.entry.configure(style='red.TCombobox')
        try:
            reg = CustomRegEx.compile(regexPattern, compFlags)
        except Exception as inst:
            self.queue.put([None, (str(inst), )])
            return self.updateGUI()
        else:
            self.matchLabel.config(text='')
            self.messageVar.set('')
            if not reg: return None
        if hasattr(reg, 'searchFlag'): reg.searchFlag = mutex
        self.entry.configure(style='TCombobox')
        tags = ['_grp%s' % x for x in range(1, reg.groups + 1)]
        for key, val in reg.groupindex.items():
            tags[val - 1] = key

        prefix = ['PosINI', 'PosFIN']
        if regexPattern.startswith('(?#<SPAN>)'):
            pini = 0
            if hasattr(reg, 'parameters'):
                prefix.extend(reg.parameters._fields)
        else:
            pini = 2

        tags = prefix + tags
        self.tree['displaycolumns']= range(pini, len(tags))
        for k, colName in enumerate(tags):
            self.tree.heading(k, text = colName)
        colBeg = len(tags)
        colEnd = len(self.tree.cget('columns'))
        for k in range(colBeg, colEnd):
            self.tree.heading(k, text = '')

        if not mutex.is_set():
            mutex.set()
            self.t = threading.Thread(name="searchThread",
                                      target=self.lengthProcess,
                                      args=(reg, content, baseIndex, mutex))
            self.t.start()
            self.activeCallBack.append(self.after(100, self.updateGUI))

    def lengthProcess(self, reg, content, baseIndex, mutex):
        k = 0
        pos = 0
        while mutex.is_set():
            try:
                match = reg.search(content, pos)
            except Exception as e:
                self.queue.put([None, (str(e), )])
                return
            if not match:
                k = -k
                break
            k += 1
            pos = match.end(0)
            self.queue.put([k, (match, baseIndex)])
        if k <= 0:
            self.queue.put([k, (None, baseIndex)])
        return

    def removeTags(self, tagIni, tagFin):
        tagColor = ['evenMatch', 'oddMatch', 'actMatch', 'group', 'hyper']
        for match in tagColor:
            self.textWidget.tag_remove(match, tagIni, tagFin)
        for button in [self.leftWing, self.rightWing]:
            button.pack_forget()
        self.matchLabel.config(text='', bg = 'SystemButtonFace')
        items = self.tree.get_children()
        self.tree.delete(*items)
        map(self.textWidget.mark_unset, items)


    def setTag(self, tag, baseIndex, match, grpIndx):
        tagIni = baseIndex + ' + %d chars'%match.start(grpIndx)
        tagFin = baseIndex + ' + %d chars'%match.end(grpIndx)
        try:
            self.textWidget.tag_add(tag, tagIni, tagFin)
        except:
            print 'exception: ' + tag + ' tagIni: ' + tagIni + ' tagFin: ' + tagFin

        ngroups  = len(match.groups())
        for key in range(1,ngroups+1):
            tagIni = baseIndex + ' + %d chars'%match.start(key)
            tagFin = baseIndex + ' + %d chars'%match.end(key)
            self.textWidget.tag_add('group', tagIni, tagFin)

        urlkeys = [key for key in match.groupdict().keys() if key.lower().endswith('url')]
        if not urlkeys and match.groupdict().has_key('label'):
            urlkeys = ['label']
        for key in urlkeys:
            tagIni = baseIndex + ' + %d chars'%match.start(key)
            tagFin = baseIndex + ' + %d chars'%match.end(key)
            self.textWidget.tag_add('hyper', tagIni, tagFin)


    def updateGUI(self):
        nProcess = 100
        k = 10000
        while k > 0 and nProcess and not self.queue.empty():
            k, args = self.queue.get()
            if k > 0:
                match, baseIndex = args
                nProcess -= 1
                tagColor = ['evenMatch', 'oddMatch']
                matchColor = tagColor[k%2]
                self.setTag(matchColor, baseIndex, match, 0)
                tagIni = self.textWidget.index(baseIndex + ' + %d chars'%match.start(0))
                iid = 'I{:03x}'.format(k)
                self.textWidget.mark_set(iid, tagIni)

                nCols = len(match.groups())
                bFlag = hasattr(match, 'parameters') and match.parameters
                if bFlag:
                    nCols += len(match.parameters)
                nCols = min(len(self.tree['columns']) - 2, nCols)
                tagValues = (match.start(0), match.end(0))
                if bFlag: tagValues += match.parameters
                tagValues += match.groups()[:nCols - len(tagValues) + 2]
                tagValues = tagValues + (len(self.tree['columns']) - len(tagValues))*('',)
                self.tree.insert('', 'end', iid, values = tagValues)     #Por revisar

                if k > 1:
                    matchStr = ' ' + str(k) + ' '
                    self.matchLabel.config(text = matchStr)
                    self.matchLabel.update()
                    continue
                self.actMatchIndx = 1
                self.matchLabel.config(text = ' 1 ', bg = 'SystemButtonFace')
                self.setTag('actMatch', baseIndex, match, 0)
                self.textWidget.tag_delete('sel')
                btState = tk.NORMAL
            elif k == 0:
                self.actMatchIndx = 0
                self.matchLabel.config(text = ' 0 de 0 ', bg = 'red')
                btState =  tk.DISABLED
            elif k is not None:     # k is an negative integer, success
                btState = tk.NORMAL
                matchStr = ' '  + str(self.actMatchIndx) + ' de ' + str(-k) + ' '
                self.matchLabel.config(text = matchStr)
                self.matchLabel.update()
            else:                   # k is None, an error has ocurred
                self.messageVar.set(args[0])
                self.matchLabel.config(text = 'Error', bg = 'red')
                btState = tk.DISABLED

            if btState == tk.DISABLED and self.leftWing.winfo_ismapped():
                for button in [self.leftWing, self.rightWing]:
                    button.pack_forget()
            elif btState == tk.NORMAL and not self.leftWing.winfo_ismapped():
                self.matchLabel.pack_forget()
                for button in [self.leftWing, self.matchLabel, self.rightWing]:
                    button.pack(side=tk.LEFT)
        if k > 0 or not self.queue.empty():
            if self.activeCallBack:
                idAfter = self.activeCallBack.pop()
                self.after_cancel(idAfter)
            self.activeCallBack.append(self.after(100, self.updateGUI))

class NavigationBar(tk.Frame):
    DEF_REQUEST_HEADERS = [
        ["User-Agent" , "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"],
        ["Accept","text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"],
        ["Accept-Encoding","gzip,deflate,sdch"],
        ["Accept-Language" , "es-ES,es;q=0.8,en;q=0.6"],
        ["Cache-Control" , "max-age=0"],
        ["Connection" , "keep-alive"]
    ]

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.urlContent = None
        self.mutex = thread.allocate_lock()
        self.activeUrl = tk.StringVar()
        self.upHistory = []
        self.downHistory = []
        self.cookies={}
        self.request_headers = []
        self.browserParam = {'user-agent':network.DESKTOP_BROWSER, 'switch_location':True, 'working-dir':'c:/testFiles'}
        self.initNetwork()
        self.makeWidgets()

    def makeWidgets(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        urlFrame = self

        iconImage = imgp.getFontAwesomeIcon
        commOptions = dict(size=24,isPhotoImage=True, color='black', aspectratio='stretch')

        self.leftIcon = leftIcon = iconImage('fa-arrow-left', **commOptions)
        self.rightIcon = rightIcon = iconImage('fa-arrow-right', **commOptions)
        self.gearIcon = gearIcon = iconImage('fa-gear', **commOptions)

        self.prevUrl = tk.Button(urlFrame, image=leftIcon, state = tk.DISABLED, font = self.customFont, text = "<", command = self.prevButton)
        self.prevUrl.pack(side = tk.LEFT)
        self.nextUrl = tk.Button(urlFrame, image=rightIcon, state = tk.DISABLED, font = self.customFont, text = ">", command = self.nxtButton)
        self.nextUrl.pack(side = tk.LEFT)
        labelUrl = tk.Label(urlFrame, text = "Actual URL:", width = 11, justify = tk.LEFT)
        labelUrl.pack(side = tk.LEFT)
        self.labelUrl = labelUrl
        self.settings = tk.Button(urlFrame, image=gearIcon, font = self.customFont, text = "S", command = self.settingComm)
        self.settings.pack(side = tk.RIGHT)
        entryUrl = tk.Entry(urlFrame, textvariable = self.activeUrl, font = self.customFont)
        entryUrl.pack(side=tk.LEFT, fill = tk.X, expand = 1 )
        entryUrl.bind('<Return>', self.returnKey)
        entryUrl.bind('<Control-o>', self.controlleftKey)

    def settingComm(self):
#         msg = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>'
#         msg += '<category label="General">\n'
#         msg += '<setting type="lsep" label ="%s" color="red"/>\n' % 'General'
#
#         genHdr = self.genHdr
#         for key, value in genHdr:
#             msg += '''<setting type="lsep" label ='%s' noline="1"/>\n''' % (key.ljust(25) + ': ' + value)
#
#         msg += '<setting type="lsep" label ="%s" color="green"/>\n' % 'Response Headers'
#         rspHdr = self.rspHdr
#         for key, value in sorted(rspHdr):
#             msg += '''<setting type="lsep" label ='%s' noline="1"/>\n''' % (key.ljust(25) + ': ' + value)
#
#         msg += '<setting type="lsep" label ="%s" color="blue"/>\n' % 'Request Headers'
#         reqHdr = self.reqHdr
#         for key, value in sorted(reqHdr):
#             msg += '''<setting type="lsep" label ='%s' noline="1"/>\n''' % (key.ljust(25) + ': ' + value)
#
#         msg += '</category>\n'
#         msg += '<category label="Headers">\n'
#         reqHdr = '|'.join(map(','.join, self.DEF_REQUEST_HEADERS))
#         msg += '''<setting id="req_headers" type="optionlst" default='%s' label="Request headers to use" columnsheadings = "Header, Value" />\n''' % reqHdr
#         msg += '</category>\n'
#         msg += '</settings>\n'

#         browserParam = {}
#         if self.request_headers: browserParam['req_headers'] = '|'.join(map(','.join, self.request_headers))
#         browser = AppSettingDialog(self, msg, isFile = False, settings = browserParam, title = 'Browser config params', dheight = 600, dwidth = 800)
#         browserParam = browser.result
#         if 'req_headers' in browserParam:
#             self.request_headers = [map(lambda x: x.strip(),record.split(',', 1)) for record in browserParam['req_headers'].split('|')]
#         else:
#             self.request_headers = []

        browser = AppSettingDialog(self, 'browserSettings.xml', settings = self.browserParam, title = 'Browser config params')
        bp = browser.result
        self.browserParam = bp
        self.initNetwork()

    def initNetwork(self):
        bp = self.browserParam
        initConf = 'curl '
        initConf += ' --user-agent "%s"' % bp['user-agent']
        initConf += ' --cookie-jar "%s"' % bp.get('cookie-jar','cookies.lwp')
        if bp.has_key('flag-output'):
            initConf += ' -o "%s"' % bp['output']
            if bp.has_key('remote-name'): initConf += ' --remote-name'
            if bp.has_key('remote-header-name'): initConf += ' --remote-header-name'
        for key in bp:
            if not key.startswith('switch_'): continue
            switch = key[len('switch_'):]
            initConf += ' --' + switch
        if bp.has_key('flag-proxy'):
            initConf += ' --proxy "%s"' % bp['proxy']
            proxy_auth = bp['proxy_auth'].split('|',1)[0]
            if proxy_auth != 'No authentication':
                initConf += ' --proxy-%s' % proxy_auth
                initConf += ' --proxy-user "%s:%s"' % (bp['proxy-user'], bp['proxy-password'])

        self.net = network.network(initConf, defDirectory = bp['working-dir'])

    def setActiveUrl(self, url):
        if url and not url.startswith('curl'):
            activeUrl = self.normUrl(self.activeUrl.get())
            url = urlparse.urljoin(activeUrl, url)
            url = self.unNormUrl(url)
        self.activeUrl.set(url)
        self.returnKey()

    def getActiveUrl(self):
        # rawUrl = self.activeUrl.get()
        # return self.net.getValuesFromUrl(rawUrl) if rawUrl else ''
        return self.net.values.url if self.net.values else ''

    def nxtButton(self, *args, **kwargs):
        if not len(self.upHistory): return
        self.prevUrl.config(state = tk.NORMAL)
        self.downHistory.append(self.upHistory.pop())
        if len(self.upHistory) == 1:
            self.nextUrl.config(state = tk.DISABLED)
        self.activeUrl.set(self.upHistory[-1])
        self.returnKey()

    def prevButton(self, *args, **kwargs):
        self.nextUrl.config(state = tk.NORMAL)
        self.upHistory.append(self.downHistory.pop())
        if not len(self.downHistory):
            self.prevUrl.config(state = tk.DISABLED)
        self.activeUrl.set(self.upHistory[-1])
        self.returnKey()

    def returnKey(self, *args, **kwargs):
        rawUrl = self.activeUrl.get()
        if not rawUrl: return
        if not self.upHistory:
            self.upHistory.append(rawUrl)
        elif rawUrl != self.upHistory[-1]:
            if len(self.upHistory) == 1:
                self.downHistory.append(self.upHistory.pop())
                self.prevUrl.config(state = tk.NORMAL)
            else:
                self.upHistory = []
                self.nextUrl.config(state = tk.DISABLED)
            self.upHistory.append(rawUrl)

        thId = thread.start_new_thread(self.importUrl, (rawUrl, self.mutex))
        self.colorAnimation()

    def controlleftKey(self, event):
        name = tkFileDialog.askopenfilename(filetypes=[('text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            name = 'file:' + urllib.pathname2url(name)
            self.activeUrl.set(name)
            self.returnKey()

    def colorAnimation(self, *args, **kwargs):
        with self.mutex:
            bFlag = not self.urlContent
        if bFlag:
            self.settings['state'] = tk.DISABLED
            colorPalette = ['-  -  -  -', '\\  /  \\  /', '/  \\  /  \\']
            actColor = self.labelUrl.cget('text')
            try:
                indx = (colorPalette.index(actColor) + 1) % (len(colorPalette))
            except:
                indx = 0
            self.labelUrl.config(text = colorPalette[indx])
            self.labelUrl.after(100, self.colorAnimation)
        else:
            self.settings['state'] = tk.NORMAL
            if isinstance(self.urlContent, Exception):
                tkMessageBox.showerror('Error', self.urlContent)
                self.urlContent = ''
            self.urlContentProcessor(self.urlContent)
            self.urlContent = None
            self.labelUrl.config(text = 'Actual URL:')

    def setUrlContentProcessor(self, processor):
        self._urlContentProcessor = processor

    def urlContentProcessor(self, data):
        if self._urlContentProcessor: return self._urlContentProcessor(data)
        pass

    def normUrl(self, url):
        match =  re.match(r'[a-zA-Z0-9]+?://', url)
        if match is None: url = 'http://' + url
        return url

    def unNormUrl(self, url):
        if url.startswith('http://'):
            url = url[7:]
        return url

    def importUrl(self, urlToOpen, mutex):
        try:
            data, resp_url = self.net.openUrl(urlToOpen)
        except Exception as e:
            self.urlContent = e
            return
        if isinstance(data, basestring):
            for match in re.finditer("\$\.cookie\('([^']+)',\s*'([^']+)",data):
                key,value = match.groups()
                self.cookies[key]=value
#             self.cookies["url_referer"] = self.values.url
        with mutex:
            resp_url = self.unNormUrl(resp_url)
            self.activeUrl.set(resp_url)
            self.urlContent = data

    def openUrl(self, urlToOpen):
        """
        http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?com.tibco.ps.pagesvc.action=portletAction&com.tibco.ps.pagesvc.targetSubscription=5d9e2b27_11de9ed172b_-74187f000001&action=buscar&tipoMercado=1&diaFecha=09&mesFecha=10&anioFecha=2015&nemo=&filtroAcciones=2
        <option\W+selected="selected"\W+value='(?P<grp1>[^']+)'>.+?</option>
        (?#<button class="yt-uix-button yt-uix-button-size-default yt-uix-button-default yt-uix-button-has-icon" .span<.*>*>)
        """

    # 31-08-04
    #v1.0.0

    # cookie_example.py
    # An example showing the usage of cookielib (New to Python 2.4) and ClientCookie

    # Copyright Michael Foord
    # You are free to modify, use and relicense this code.
    # No warranty express or implied for the accuracy, fitness to purpose or otherwise for this code....
    # Use at your own risk !!!

    # If you have any bug reports, questions or suggestions please contact me.
    # If you would like to be notified of bugfixes/updates then please contact me and I'll add you to my mailing list.
    # E-mail michael AT foord DOT me DOT uk
    # Maintained at www.voidspace.org.uk/atlantibots/pythonutils.html

        COOKIEFILE = 'cookies.lwp'          # the path and filename that you want to use to save your cookies in
        import os.path

        cj = None
        cookielib = None

        import cookielib
        import urllib2
        cj = cookielib.LWPCookieJar()       # This is a subclass of FileCookieJar that has useful load and save methods
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        ####################################################
        # We've now imported the relevant library - whichever library is being used urlopen is bound to the right function for retrieving URLs
        # Request is bound to the right function for creating Request objects
        # Let's load the cookies, if they exist.

        if cj != None and os.path.isfile(COOKIEFILE):                                  # now we have to install our CookieJar so that it is used as the default CookieProcessor in the default opener handler
                cj.load(COOKIEFILE)

        request_headers = self.request_headers or self.DEF_REQUEST_HEADERS

        referer = 'http://www.peliculaspepito.com/'
        if self.downHistory:
            referer = self.downHistory[-1]
        request_headers.append(["Referer" , referer])

        headers = dict(request_headers)

        urlToOpen, custHdr = urlToOpen.partition('<headers>')[0:3:2]
        if custHdr:
            custHdr = urlparse.parse_qs(custHdr)
            for key in custHdr:
                headers[key] = custHdr[key][0]

        urlToOpen, postData = urlToOpen.partition('<post>')[0:3:2]
        postData = postData or None

        try:
            req = urllib2.Request(urlToOpen, postData or None, headers)
            url = opener.open(req)
        except Exception as e:
            data = e
        else:
            self.genHdr = []
#             self.genHdr.append(('Remote Address', socket.gethostbyname(req.get_host()) + ':' + str(socket.getservbyname(req.get_type()))))
#             self.genHdr.append(('Request Url', req.get_full_url()))
#             self.genHdr.append(('Request Method', req.get_method()))
#             self.genHdr.append(('Status Code', str(url.getcode())))
            self.reqHdr = req.header_items()
            self.rspHdr = url.headers.items()
            self.activeUrl.set(self.unNormUrl(url.geturl()))
            data = url.read()
            if url.info().get('Content-Encoding') == 'gzip':
                import StringIO
                compressedstream = StringIO.StringIO(data)
                import gzip
                gzipper = gzip.GzipFile(fileobj=compressedstream)
                data = gzipper.read()
                gzipper.close()
            url.close()
        if cj != None: cj.save(COOKIEFILE)                     # save the cookies again
        return data


class ScrolledList(tk.Frame):
    def __init__(self, master, threadSource = None):
        tk.Frame.__init__(self, master)
        self.message = tk.StringVar()
        self.threadSource = threadSource or self.menuSampleTest()
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.makeWidgets()

    def menuSampleTest(self):
        xbmcMenu = menuThreads.menuThreads()
        params = {'url':'http://www.movie25.com', 'regexp':'<li><a href=\"(?P<url>.+?)\" title=\"(?P<label>.+?)\">'}
        xbmcMenu.createThread('thread', 'Movies', 'movies', params = params)
        params = {'url':'http://www.movie25.com/new-releases/', 'regexp':'<h1><a href="(?P<url>.+?)".+?>\s*(?P<label>.+?)\s*</a></h1>', 'compflags':'re.DOTALL', 'nextregexp':"</font>&nbsp;<a href='(?P<url>.+?)'"}
        xbmcMenu.createThread('thread', 'List', 'list', params = params)
        params = {'url':'http://www.movie25.com/murder-on-the-home-front-2013-47092.html', 'regexp':'<li class="link_name">\s*(?P<label>.+?)\s*</li>.+?<span><a href="(?P<url>.+?)"', 'compflags':'re.DOTALL'}
        xbmcMenu.createThread('thread', 'UrlResolvers', 'urlresolvers', params = params)
        params = {'url':'http://www.movie25.tw/watch-school-dance-2014-48108-1171666.html', 'regexp':'onclick="location.href=\'(?P<url>.+?)\'"  value="Click Here to Play" />', 'compflags':'re.DOTALL'}
        xbmcMenu.setThreadParams('media', params)

        xbmcMenu.setNextThread('movies', 'list')
        xbmcMenu.setNextThread('list', 'urlresolvers')
        xbmcMenu.setNextThread('urlresolvers', 'media')
        return xbmcMenu

    def select(self, index):
        self.listbox.focus_set()
        self.listbox.activate(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)

    def up_event(self, event):
        selItem = self.listbox.index("active")
        if selItem == 0:
            selItem = self.listbox.size() - 1
        else:
            selItem -= 1
        self.select(selItem)
        return "break"

    def down_event(self, event):
        selItem = self.listbox.index("active")
        if selItem == self.listbox.size() - 1:
            selItem = 0
        else:
            selItem += 1
        self.select(selItem)
        return "break"

    def handleList(self, event):
        index = self.listbox.curselection()                # on list double-click
        self.runCommand(index)                             # and call action here
                                                           # or get(ACTIVE)

    def makeWidgets(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        globFrame = tk.Frame(self)
        globFrame.pack(fill = tk.BOTH, expand = tk.YES)
        frame = tk.Frame(globFrame, relief = tk.SUNKEN)
        frame.pack(side = tk.LEFT, fill = tk.Y)
        sbar = tk.Scrollbar(frame)
        listBox = tk.Listbox(frame, selectmode = 'SINGLE', width = 50, relief=tk.SUNKEN, font = self.customFont)
        sbar.config(command=listBox.yview)                    # xlink sbar and list
        listBox.config(yscrollcommand=sbar.set)               # move one moves other
        sbar.pack(side=tk.RIGHT, fill=tk.Y)                      # pack first=clip last
        listBox.pack(side=tk.LEFT, fill=tk.BOTH)        # list clipped first
        listBox.bind('<<ListboxSelect>>', self.handleList)           # set event handler
        listBox.event_add('<<Execute Option>>','<Return>','<Double-Button-1>')
        listBox.bind('<<Execute Option>>', self.executeOption)
        listBox.bind('<Key-Up>', self.up_event)
        listBox.bind('<Key-Down>', self.down_event)
        self.listbox = listBox

        labelPane = tk.Label(globFrame, textvariable = self.message, relief=tk.SUNKEN)
        labelPane.pack(side = tk.LEFT, fill = tk.BOTH, expand = tk.YES)

    def runCommand(self, index):                       # redefine me lower
        label = self.listbox.get(index)                # fetch selection text
        texto = 'You selected: \n' + label
        index = int(index[0])
        for key in sorted(self.options[index].keys()):
            texto = texto + '\n' + key + ' = \t' + str(self.options[index][key])
        self.message.set(texto)

    def initGlobals(self):
        theGlobals = {}
        exec 'import os' in theGlobals
        exec 'import urllib' in theGlobals
        exec 'import re' in theGlobals
        exec 'from basicFunc import openUrl, parseUrlContent, getMenu' in theGlobals
        exec 'from basicFunc import getMenuHeaderFooter, processHeaderFooter'  in theGlobals
        exec 'from basicFunc import LISTITEM_KEYS, INFOLABELS_KEYS' in theGlobals
#         theGlobals['getMenu'] = self.getMenu
#         theGlobals['parseUrlContent'] = self.parseUrlContent
        theGlobals['args'] = {}
        siteAPI = ''
        siteAPI += self.threadSource.scriptSource('rootmenu')
        siteAPI += self.threadSource.scriptSource('media', reverse = True)
        with open('siteAPI.py', 'w') as f:
            f.write(siteAPI)
        siteApiSrc = compile(siteAPI, 'siteAPI.py', 'exec')
        exec siteApiSrc in theGlobals
        self.theGlobals = theGlobals

    def initFrameExec(self):
#         self.threadSource = threadSource
        knotId = self.threadSource.threadDef
        if self.threadSource.getThreadAttr(knotId, 'type') == 'thread':
            url = self.threadSource.getThreadParam(knotId, 'url')
            option['url'] = [ url ]
            self.theGlobals['args'] = {'url':option['url']}
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.optHistory = [[0, option]]
        self.fillListBox(knotId)


    def executeOption(self, event = None):
        index = int(self.listbox.curselection()[0])              # on list double-click
        option = self.options[index]
        pointer = self.prevPointer
        if option['label'] == "NotImplemented option": return
        if option['label'] != '..':
            if index != self.optHistory[pointer][0]:
                self.optHistory[pointer][0] = index
                self.optHistory = self.optHistory[:pointer+1]
            if pointer == len(self.optHistory)-1:
                self.optHistory.append([0, {}])
                self.optHistory[-1][1].update(option)
            pointer += 1
        else:
            pointer -= 1
        self.prevPointer = pointer
        selItem = self.optHistory[pointer][0]
        if option['isFolder']:
            knotId = option.pop('menu')
            self.theGlobals['args'] = option
            self.fillListBox(knotId, selItem)

    def fillListBox(self, threadKnot, selItem = 0):
        fillFunc = 'menuContent = ' + threadKnot + '()'
        if threadKnot != 'media':
            exec fillFunc in self.theGlobals
            menuContent = self.theGlobals.pop('menuContent')
        else:
            menuContent = []
        options = []
        for elem in menuContent:
            for key in elem[0].keys():
                if key != 'menu':
                    elem[0][key] = [str(elem[0][key])]
            options.append(elem[0])
            options[-1].update(elem[1])

        if threadKnot == 'media':
            if options:
                options[0]['label'] = 'url media'
            else:
                options.append({'label':'url media'})

        if self.prevPointer:
            head = {}
            pointer = self.prevPointer - 1
            head.update(self.optHistory[pointer][1])
            head['label'] = '..'
            options.insert(0, head)
        self.options = options
        self.listbox.delete('0', 'end')
        for pos, item in enumerate(options):                              # add to listbox
            self.listbox.insert(pos, item['label'])                        # or insert(END,label)
        self.select(selItem)

class StatusBar(tk.Frame):
    def __init__(self, master, statusList):
        tk.Frame.__init__(self, master)
        self.setGUI(statusList)

    def setGUI(self, statusList):
        kwargs = dict(bd=3, relief=tk.SUNKEN, height=1, width=40, anchor=tk.NW, padx=5)
        frame = tk.Frame(self, bd = 5)
        frame.pack(side = tk.TOP, fill = tk.X)
        label = tk.Label(frame, text = statusList[0][0], bd = 3)
        label.pack(side = tk.LEFT)
        kwargs['textvariable'] = statusList[0][1]
        label = tk.Label(frame, **kwargs)
        label.pack(side = tk.LEFT)
        label = tk.Label(frame, text = statusList[1][0], bd = 3)
        label.pack(side = tk.LEFT)
        kwargs['textvariable'] = statusList[1][1]
        label = tk.Label(frame, **kwargs)
        label.pack(side=tk.LEFT, fill = tk.X, expand = 1)
        kwargs['textvariable'] = statusList[2][1]
        label = tk.Label(frame, **kwargs)
        label.pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        label = tk.Label(frame, text = statusList[2][0], bd = 3)
        label.pack(side = tk.RIGHT)

class PythonEditor(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        self.prompt =''
        self.cellInput = ''
        self.hyperlinkManager = None

        self.scrbar = scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        textw = tk.Text(self, font = self.customFont, tabs=('1.5c'))
        textw.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textw.yview)

        self.textw = textw
        textw.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        textw.see('end')
        textw.event_add('<<CursorlineOff>>','<Up>','<Down>','<Next>','<Prior>','<Button-1>')
        textw.event_add('<<CursorlineOn>>','<KeyRelease-Up>','<KeyRelease-Down>','<KeyRelease-Next>','<KeyRelease-Prior>','<ButtonRelease-1>')
        textw.event_add('<<CopyEvent>>','<Control-C>','<Control-c>')
        textw.event_add('<<PasteEvent>>','<Control-V>','<Control-v>')
        textw.event_add('<<CutEvent>>','<Control-X>','<Control-x>')
        textw.event_add('<<SelAllEvent>>','<Control-A>','<Control-a>')
        textw.event_add('<<NavigationEvent>>',
                        '<Home>', '<Control-Home>', '<Shift-Home>',
                        '<End>','<Control-End>', '<Shift-End>',
                        '<Control-Left>', '<Shift-Control-Left>',
                        '<Control-Right>', '<Shift-Control-Right>')

        textw.tag_configure('cursorLine', background = 'alice blue')
        textw.tag_configure('evenMatch', background = 'yellow')
        textw.tag_configure('oddMatch', background = 'red')
        textw.tag_configure('actMatch', background = 'light green')
        textw.tag_configure('group', foreground = 'blue')
        textw.tag_configure("hyper", foreground="blue", underline=1)
        textw.tag_configure(tk.SEL, foreground = 'white', background='blue')
        textw.tag_raise(tk.SEL)

        textw.tag_bind("hyper", "<Enter>", self._enter)
        textw.tag_bind("hyper", "<Leave>", self._leave)
        textw.tag_bind("hyper", "<Button-1>", self._click)



        self.dispPrompt()
        textw.bind('<<CopyEvent>>', self.selCopy)
        textw.bind('<<PasteEvent>>', self.selPaste)
        textw.bind('<<CutEvent>>', self.selCut)
        textw.bind('<<SelAllEvent>>',self.selAll)
        textw.bind('<<CursorlineOff>>', self.onUpPress)
        textw.bind('<<CursorlineOn>>', self.onUpRelease)
        textw.bind('<<NavigationEvent>>', self.moveCursor)

    def moveCursor(self, event):
        control_key = (event.state & 0x0004)
        shift_key = (event.state & 0x0001)
        posIni = self.textw.index(tk.INSERT)
        if event.keysym == 'Home' and control_key:     #<Control-Home>
            posFin = '1.0'
        elif event.keysym == 'End' and control_key:    #<Control-End>
            posFin = tk.END
        elif event.keysym == 'Home' and not control_key:                    #<Home>
            posFin = '%s linestart' % posIni
        elif event.keysym == 'End' and not control_key:                     #<End>
            posFin = '%s lineend' % posIni
        elif event.keysym == 'Left' and control_key:   #<Control-Left>
            posFin = '%s wordstart' % posIni
        elif event.keysym == 'Right' and control_key:  #<Control-Right>
            posFin = '%s wordend' % posIni

        if shift_key:
            if not self.textw.tag_ranges('sel'): self.textw.mark_set('tk::anchor1', posIni)
            self.textw.tag_add('sel', posIni, posFin)
        self.textw.see(posFin)
        self.textw.mark_set('insert', posFin)

    def _enter(self, event):
        self.textw.config(cursor="hand2")

    def _leave(self, event):
        self.textw.config(cursor="")

    def _click(self, event):
        if 'hyper' in self.textw.tag_names(tk.CURRENT):
            tagRange = self.textw.tag_prevrange('hyper', tk.CURRENT)
            texto = self.textw.get(*tagRange)
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

    def getSelRange(self, tagName = 'sel'):
        textw = self.textw
        try:
            return textw.tag_ranges(tagName)
        except tk.TclError:
            return None

    def colorMatch(self, baseIndex, match, matchColor, frstMatch = False):
        tagIni = baseIndex + ' + %d chars'%match.start(0)
        tagFin = baseIndex + ' + %d chars'%match.end(0)
        try:
            self.textw.tag_add(matchColor, tagIni, tagFin)
        except:
            print 'exception: ' + matchColor + ' tagIni: ' + tagIni + ' tagFin: ' + tagFin
        # self.textw.tag_add('matchTag', tagIni, tagFin)
        if frstMatch:
            self.textw.tag_add('actMatch', tagIni, tagFin)
        return


    def getContent(self, posIni = '1.0', posFin = 'end'):
        textw = self.textw
        return textw.get(posIni, posFin)

    def setContent(self,text):
        self.textw.delete('1.0','end')
        if text:
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

class RegexpFrame(tk.Frame):
    def __init__(self, master, xbmcThreads, messageVar):
        tk.Frame.__init__(self, master)
        self.xbmcThreads = xbmcThreads
        self.linkedPane = None
        self.dropDownFiler = None
        self.popUpMenu = None
        self.state = None
        self.queue = Queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'

        self.messageVar = messageVar
        self.setGUI()

    def initFrameExec(self, refreshFlag=False):
        xbmcThreads = self.xbmcThreads
        getThParam = xbmcThreads.getThreadParam
        activeKnotId = xbmcThreads.threadDef
        actState = (getThParam(activeKnotId, 'url'), getThParam(activeKnotId, 'regexp'))
        if refreshFlag and self.state == actState: return
        urlToOpen = 'plugin://plugin.video?menu=%s' % activeKnotId
        rgfrm = self.regexBar
        self.setActiveUrl(urlToOpen)
        if actState != ('', ''):
            self.state = actState

    def setGUI(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)

        self.urlFrame = NavigationBar(self)
        self.urlFrame.pack(fill = tk.X)
        self.urlFrame.setUrlContentProcessor(self.setContent)

        self.regexBar = RegexpBar(self, self.messageVar)
        self.regexBar.pack(fill = tk.X)
        self.regexBar.setZoomManager(self.zoom)

        frame2 = collapsingFrame.collapsingFrame(self, buttConf = 'mRM')
        frame2.pack(fill = tk.BOTH, expand = 1)
        self.txtEditor = PythonEditor(frame2.frstWidget)
        self.tree = idewidgets.TreeList(frame2.scndWidget, displaycolumns = '#all',
                                 show = 'headings', columns = ('posINI', 'posFIN', 'var0','var1','var2','var3','var4','var5'))
        self.tree.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

        self.txtEditor.setKeyHandler(self)
        self.txtEditor.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        self.txtEditor.setHyperlinkManager(self.hyperLnkMngr)
        self.regexBar.setTextWidget(self.txtEditor.textw)
        self.regexBar.setTreeWidget(self.tree)
        self.txtEditor.textw.bind('<Button-3>',self.do_popup)

    def isZoomed(self):
        return self.regexBar.butKeyMaker.cget('text') != 'ZoomIn'

    def zoom(self, btnText):
        if btnText == 'ZoomIn':
            selRange = self.txtEditor.getSelRange() or self.txtEditor.getSelRange('actMatch')
            if not selRange: return False
            zinBuff = [self.txtEditor.scrbar.get(), selRange]
            textw = self.txtEditor.textw
            height = textw.winfo_height()
            zinBuff.append((textw.index(tk.INSERT), textw.index('@0,%s' % (height/2))))
            rgxFlag = not self.txtEditor.getSelRange()
            texto = self.txtEditor.getContent(*selRange)
            self.setContent(texto, False)
            regExPat = self.getRegexpPattern()
            prefix = self.regexBar.cbIndex.get()
            zinBuff.append((prefix, regExPat))
            self.regexBar.anchorPos.append(zinBuff)
            self.regexBar.butAnchor['state'] = tk.DISABLED
            if regExPat.startswith('(?#<SPAN>)'): self.setActiveUrl()
            return True
        else:
            self.urlFrame.returnKey()
            return False
        
    def setDropDownFiler(self, callbckFunc):
        self.regexBar.setDropDownFiler(callbckFunc) 
                
    def do_popup(self, event):
        if not self.popUpMenu: return
        popup = self.popUpMenu()        
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()
            
    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu


    def keyHandler(self,event):
        textw =  event.widget
        if textw == self.txtEditor.textw and event.keysym not in  ['Left', 'Right', 'Up','Down','Next','Prior','Button-1']:
            return "break"

    def getSelRange(self, tagName = 'sel'):
        return self.txtEditor.getSelRange(tagName)

    def setContent(self, data, newUrl = True):
        self.txtEditor.setContent(data)
        self.regexBar.getPatternMatch()
        if self.regexBar.getZoomType() == 'ZoomOut' and (len(self.regexBar.anchorPos) - self.regexBar.anchor.get()) == 1:
            zinBuff = self.regexBar.anchorPos.pop()
            textw = self.txtEditor.textw
            posIni, posFin = zinBuff[1]
            textw.mark_set('tk::anchor1', posIni)
            textw.tag_add('sel', posIni, posFin)
            insPos, wndFIN = zinBuff[2]
            textw.mark_set(tk.INSERT, insPos)
            textw.see(wndFIN)
            prefix, regExPat = zinBuff[3]
            self.regexBar.cbIndex.set(prefix)
            self.setRegexpPattern(regExPat)
            self.regexBar.butAnchor['state'] = tk.NORMAL
        if newUrl: self.regexBar.setZoomType('ZoomIn')

        
    def pasteFromClipboard(self, event = None):
        textw = self.txtEditor.textw
        try:
            data = textw.selection_get(selection = 'CLIPBOARD')
            self.setContent(data)
        except tk.TclError:
            pass
        else:
            self.urlFrame.setActiveUrl('')
    def getContent(self, posIni = '1.0', posFin = 'end'):
        return self.txtEditor.getContent(posIni, posFin)
            
    def getRegexpPattern(self, *args, **kwargs):
        return self.regexBar.getRegexpPattern(*args, **kwargs)

    def getCompFlags(self):
        return self.regexBar.getCompFlags()
    
    def setRegexpPattern(self, regexp):
        self.regexBar.setRegexpPattern(regexp)
        
    def setCompFlags(self, compflags):
        self.regexBar.setCompFlags(compflags)            

    def getNxtMenu(self, threadId, urlout):
        cbIndx = self.regexBar.cbIndex.get()
        m = re.search(r'<[^-]+-([^-]+)-[^-]+>', cbIndx)
        if m: return m.group(1)
        xbmcThreads = self.xbmcThreads
        defValue = xbmcThreads.getThreadAttr(threadId, 'up')
        discrim = xbmcThreads.getThreadParam(threadId, 'discrim')
        if discrim:
            disc = xbmcThreads.getThreadParam(threadId, discrim)
            listaDisc = [(disc, threadId)] if disc else []
            listaMenu = [xbmcThreads.getThreadAttr(elem, 'name') for elem in xbmcThreads.getRawChildren(threadId) if xbmcThreads.getThreadAttr(elem, 'type') == 'link']
            for elem in listaMenu:
                params = xbmcThreads.parseThreads[elem]['params']
                listaDisc.extend([(disc, elem) for key, disc in params.items() if key.startswith(discrim)])
            discrimDict = dict(listaDisc)
            if discrim.startswith('urlout'):
                toTest = urlout
            elif discrim.startswith('urlin'):
                toTest = self.urlFrame.getActiveUrl()
            elif discrim.startswith('option'):
                iid = self.regexBar.getBorderTags('current')[0][1:]
                toTest = str(int(iid, 16) - 1)
            else:
                return defValue
            for key, value in discrimDict.items():
                if key in toTest:
                    defValue = value
                    break
        return defValue

    def hyperLnkMngr(self, url):
        regexp = self.getRegexpPattern(withFlags=True)
        if not '(?#<SPAN>)' in regexp:
            baseurl = self.urlFrame.getActiveUrl()
            url = urlparse.urljoin(baseurl, url)
        xbmcThreads = self.xbmcThreads
        activeKnotId = xbmcThreads.threadDef
        menuId = xbmcThreads.getThreadAttr(activeKnotId, 'up')
        urlsplit = urlparse.urlsplit(url)
        content = ''
        if urlsplit.netloc:
            query = dict(urlparse.parse_qsl(urlsplit.query))
            menu = query.get('menu')
            if urlsplit.scheme == 'plugin' and xbmcThreads.getThreadAttr(menu, 'type') == 'thread':
                url = xbmcThreads.getThreadParam(menu, 'url')

            if not url.startswith('plugin://'):
                self.urlFrame.setActiveUrl(url)
                if urlsplit.scheme == 'plugin':
                    menuId = menu
                else:
                    menuId = self.getNxtMenu(activeKnotId, url)
                rgxexp = '(?#<rexp-{0}>){1}'.format(menuId, xbmcThreads.getThreadParam(menuId, 'regexp'))
            else:
                self.urlFrame.setActiveUrl('')
                menuId = menu
                content = ''
                for node in xbmcThreads.getChildren(menuId):
                    content += 'name=%s, url=plugin://plugin.video?menu=%s\n' % (xbmcThreads.getThreadAttr(node, 'name'), node)
                rgxexp = xbmcThreads.getThreadParam(menuId, 'regexp')
        else:
            menuId = xbmcThreads.getThreadAttr(activeKnotId, 'up')
            textWidget = self.txtEditor.textw
            tagnames = textWidget.tag_names('current')
            nxtTag = set(['oddMatch', 'evenMatch']).intersection(tagnames).pop()
            srange = textWidget.tag_prevrange(nxtTag, 'current')
            content = self.getContent(*srange)
            rgxexp = '(?#<rexp-{0}>){1}'.format(menuId, xbmcThreads.getThreadParam(menuId, 'regexp'))
            pass
        if menuId:
            compFlags = xbmcThreads.getThreadParam(menuId, 'compflags')
            self.setCompFlags(compFlags)
            self.setRegexpPattern(rgxexp)
        self.setContent(content)

        xbmcThreads.threadDef = menuId
        if self.linkedPane: self.linkedPane.refreshPaneInfo()

    def setActiveUrl(self, url = None):
        if url and self.regexBar.anchorPos:
            self.regexBar.anchorPos = []
            self.regexBar.anchor.set(0)
        rgxNode = None
        rgfrm = self.regexBar
        theValues = rgfrm.dropDownFiler()
        ndxpos = [val[0] for val in theValues]
        if not url or not url.startswith('plugin://'):
            rgxNode = rgfrm.cbIndex.get()
            if rgxNode: rgfrm.entry.set('')
            if url: self.urlFrame.setActiveUrl(url)
            if rgxNode:
                actpos = ndxpos.index(rgxNode)
                rgxNode = theValues[actpos][2]
        else:               # Cuando se trata de un List Node
            rgfrm.cbIndex.set('')
            self.regexBar.removeTags('1.0', 'end')
            query = urlparse.urlsplit(url).query
            query = dict(urlparse.parse_qsl(query))
            activeKnotId = query['menu']
            xbmcThreads = self.xbmcThreads
            self.setRegexpPattern('')
            if xbmcThreads.getThreadAttr(activeKnotId, 'type') == 'list':
                content = ''
                for node in xbmcThreads.getChildren(activeKnotId):
                    if node.endswith('_lnk'):
                        node = xbmcThreads.getThreadAttr(node, 'name')
                    content += 'name=%s, url=plugin://plugin.video?menu=%s\n' % (xbmcThreads.getThreadAttr(node, 'name'), node)
                self.setRegexpPattern(r'name=(?P<label>.+?), url=(?P<url>.+?)\s')
                self.setCompFlags('')
                self.setContent(content)
                return
            else:
                urlToOpen = query.get('url') or xbmcThreads.getThreadParam(activeKnotId, 'url')
                if not urlToOpen: return
                self.urlFrame.setActiveUrl(urlToOpen)
                rgxNode = '(?#<rexp-%s>)' % activeKnotId
                compFlags = xbmcThreads.getThreadParam(activeKnotId, 'compflags')
                self.setCompFlags(compFlags)
                self.regexBar.fillDropDownLst()
        if rgxNode:
            nxtpos = ndxpos.index(rgxNode)
            rgfrm.entry.current(nxtpos)


    def getActiveUrl(self):
        return self.urlFrame.getActiveUrl()
        
class NodeEditFrame(tk.Frame):
    def __init__(self, master = None, xmlFile = 'NodeSettingFile.xml', dheight = 600, dwidth = 400):
        tk.Frame.__init__(self, master, height = dheight, width = dwidth)
        self.root = ET.parse(xmlFile).getroot()
        self.rightPane = None
        self.settings = None
        self.setGUI()
        self.notifyChangeTo = None
        
    def setNotifyChange(self, notifyto):
        self.notifyChangeTo = notifyto
        
    def setGUI(self):
        bottomPane = tk.Frame(self, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.BOTTOM, fill = tk.X)
        for label in ['Discard', 'Apply']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, width = 20, command = lambda action = label.lower(): self.onAction(action))
            boton.pack(side = tk.RIGHT)
        label = tk.Label(bottomPane, name = 'message', text = '')
        label.pack(side = tk.LEFT, fill = tk.X, expand = 1)
        self.bottomPane = bottomPane
            
    def onAction(self, action):
        toProcess = self.rightPane.getChangeSettings(dict(self.settings))
        if action == 'apply':
            self.processChangedSettings(toProcess)
        elif action == 'discard':
            if not toProcess: return
            reset = toProcess.pop('reset')
            toProcess.update([(key, 1) for key in reset])
            filterFlag = lambda widget: (hasattr(widget, 'id') and toProcess.has_key(widget.id)) 
            widgets = [(widget.id, widget) for child, widget in self.rightPane.frame.children.items() if filterFlag(widget)]
            for key, widget in widgets:
                if self.settings.has_key(key):
                    widget.setValue(self.settings[key])
                else:
                    widget.setValue(widget.default)
        
    def processChangedSettings(self, changedSettings):
        if not changedSettings: return
        nodeId = self.settings['nodeId']
        nodeParams = self.xbmcThreads.getThreadAttr(nodeId,'params')
        parameters = {}
        
        if changedSettings.has_key('otherparameters') or 'otherparameters' in changedSettings['reset']:
            if self.settings.has_key('otherparameters'):
                oldOther = [tuple(elem.split(',')) for elem in self.settings['otherparameters'].split('|')]
                for key, value in oldOther:
                    nodeParams.pop(key)
        for key in changedSettings.pop('reset'):
            self.settings.pop(key)
            if nodeParams.has_key(key): nodeParams.pop(key)
        if changedSettings.get('otherparameters', None):
#             if self.settings.has_key('otherparameters'):
#                 oldOther = [tuple(elem.split(',')) for elem in self.settings['otherparameters'].split('|')]
#                 for key, value in oldOther:
#                     nodeParams.pop(key)
            otherParameters = [tuple(elem.split(',')) for elem in changedSettings['otherparameters'].split('|')]
            parameters.update(otherParameters)
        for elem in  set(changedSettings.keys()).difference(['otherparameters', 'nodeId', 'upmenu', 'name']):
            parameters[elem] = changedSettings[elem]
        if parameters: nodeParams.update(parameters)

        nodeFlag = nodeId in ['media', 'rootmenu']
        if nodeFlag:
            for key in ['nodeId', 'name', 'upmenu']: 
                if changedSettings.has_key(key): changedSettings.pop('nodeId')

        lstChanged = []
        if changedSettings.has_key('nodeId'):
            lstChanged.append(self.xbmcThreads.getDotPath(self.settings['nodeId']))
            self.xbmcThreads.rename(self.settings['nodeId'], changedSettings['nodeId'])
            lstChanged.append(self.xbmcThreads.getDotPath(changedSettings['nodeId']))
            nodeId = changedSettings['nodeId']
        if changedSettings.has_key('name'):
            self.xbmcThreads.parseThreads[nodeId]['name'] = changedSettings['name']
        if changedSettings.has_key('upmenu') and changedSettings['upmenu'] != self.settings['up']:
            upmenu = changedSettings['upmenu']
            kType = self.xbmcThreads.getThreadAttr(nodeId, 'type')
            threadIn = (upmenu, nodeId) if kType == 'list' else (nodeId, upmenu)
            lstChanged.append(self.xbmcThreads.getDotPath(nodeId))
            self.xbmcThreads.setNextThread(*threadIn)
            lstChanged.append(self.xbmcThreads.getDotPath(nodeId))
        self.settings.update(changedSettings)
        if self.notifyChangeTo: self.notifyChangeTo(True, lstChanged)

    def initFrameExec(self, xbmcThreads, param = False):
        self.xbmcThreads = xbmcThreads
        if self.rightPane: self.rightPane.forget()
        activeNodeId = xbmcThreads.threadDef
        nodeType = self.xbmcThreads.getThreadAttr(activeNodeId, 'type')
        srchStr = './/category[@label="' + nodeType + '"]'
        nodeConfigData = self.root.findall(srchStr)
        if not nodeConfigData: return
        nodeConfigData = nodeConfigData[0]
        settings = self.getNodeSettings(activeNodeId, nodeType, nodeConfigData)
        self.settings = settings
        self.rightPane = scrolledFrame(self, settings, nodeConfigData)
        self.rightPane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        btnState = self.xbmcThreads.getThreadParam(activeNodeId, 'enabled') == None
        message = '' if btnState else 'Code Locked'
        btnState = tk.NORMAL if btnState else tk.DISABLED
        self.bottomPane.children['apply'].configure(state = btnState)
        self.bottomPane.children['discard'].configure(state = btnState)
        self.bottomPane.children['message'].configure(text = message)
        
        
    def getNodeSettings(self, nodeId, nodeType, nodeConfigData):
        nodeDataIds = [key.get('id') for key in nodeConfigData.findall('setting') if key.get('id', None)]
        settings = dict(self.xbmcThreads.parseThreads[nodeId])
        params = settings.pop('params')
        settings['nodeId'] = nodeId
        if settings.has_key('up'):
            upMenu = ''
            if nodeType == 'list':
                lista = [elem for elem in self.xbmcThreads.getSameTypeNodes('rootmenu') if not elem.endswith('_lnk')]
                upMenu = '|'.join(sorted(lista))
            elif nodeType == 'thread':
                upMenu = '|'.join(sorted(self.xbmcThreads.getSameTypeNodes('media'))) if nodeId != 'media' else '' 
            upMenu = settings['up'] + '|' + upMenu
            settings['upmenu'] = upMenu
        other = set(params.keys()).difference(nodeDataIds)
        if len(other):
            params = dict(params)
            otherParameters = '|'.join([key + ', ' + str(params.pop(key)) for key in other])
            settings['otherparameters'] = otherParameters
        settings.update(params)
        return settings

class addonFilesViewer(collapsingFrame.collapsingFrame):
    def __init__(self, master):
        collapsingFrame.collapsingFrame.__init__(self, master, tk.HORIZONTAL, buttConf = 'mRM')
        self.pack_propagate(flag = False)
        
        self.sintaxEditor = SintaxEditor.SintaxEditor(self.frstWidget)
        self.sintaxEditor.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        self.textw = self.sintaxEditor.textw

        self.kodiFrame = KodiLog.kodiLog(self.scndWidget)
        self.kodiFrame.config(height = 200)
        self.kodiFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        self.kodiFrame.pack_propagate(flag = False)
#         self.collapseCommand(0)

    
    def setHyperlinkManager(self, hyperLinkProcessor):
        self.kodiFrame.setHyperlinkManager(hyperLinkProcessor)

    def initFrameExec(self, refreshFlag=False):
        pass
    
    def __getattr__(self, attr):
        if attr != 'sintaxEditor': return getattr(self.sintaxEditor, attr)
        else:  raise AttributeError, attr

class parseTree(tk.Frame):
    def __init__(self, master, xbmcThread):
        tk.Frame.__init__(self, master)
        self.setXbmcThread(xbmcThread)
        self.popUpMenu = None
        self.setGUI()
        
    def setXbmcThread(self, xbmcThread):
        self.xbmcThread = xbmcThread
        self.refreshFlag = True
        
    def setGUI(self):
        treeview = ttk.Treeview(self, show = 'tree', columns = ('name', ), displaycolumns = ())
        treeview.pack(fill = tk.BOTH, expand = tk.YES)
        treeview.event_add('<<myEvent>>','<Double-1>','<Return>')
        treeview.bind('<Button-3>',self.do_popup)
        treeview.tag_configure('activeThread', background = 'light green')
        self.treeview = treeview
        self.actTreeSel = None
        
    def refreshPaneInfo(self):
        if self.refreshFlag and self.xbmcThread:
            if self.treeview.exists('rootmenu'): self.treeview.delete('rootmenu')
            if self.treeview.exists('media'): self.treeview.delete('media')
            self.registerTreeNodes('rootmenu')
            self.registerTreeNodes('media')
        self.refreshFlag = False
        self.activeNode = None
        self.setActualKnot()
    
    def getPopUpMenu(self, threadId = None):
        popup = tk.Menu(self, tearoff = 0)
        if threadId: popup.add_command(label = threadId)
        popup.add_command(label = 'Set as ActiveKnot', command = self.onTreeSelProc)
        popup.add_command(label = 'Previous')
        popup.add_separator()
        popup.add_command(label = 'Home')
        return popup
    
    def do_popup(self, event):
        if not self.popUpMenu: return
        threadId = self.treeview.identify_row(event.y)
        self.xbmcThread.threadDef = threadId.rsplit('.', 1)[1] if threadId.find('.') != -1 else threadId
        self.setSelection(threadId)
        popup = self.popUpMenu()        
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()

            
    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu

    def setOnTreeSelProc(self, onTreeSelProc):
        self.onTreeSelProc = onTreeSelProc 
        self.treeview.bind('<<myEvent>>', self.onTreeSelProc)
        
    def setActualKnot(self):
        if not self.xbmcThread: return
        if self.xbmcThread.existsThread(self.activeNode) and self.activeNode != self.xbmcThread.threadDef:
            iid = self.getAbsoluteId(self.activeNode, absFlag = False)
            tags = self.treeview.item(iid, 'tags')
            tags = [tag for tag in tags if tag != 'activeThread']
            self.treeview.item(iid, tags = tags)
            
        if self.xbmcThread.threadDef:
            iid = self.getAbsoluteId(self.xbmcThread.threadDef, absFlag = False)
            tags = self.treeview.item(iid, 'tags')
            tags = list(tags).append('activeThread') if tags else ('activeThread',)
            self.treeview.item(iid, tags = tags)
            self.activeNode = self.xbmcThread.threadDef      
        
    def refreshTreeInfo(self, activeThread = None, lstChanged = None):
        if not activeThread: activeThread = self.xbmcThread.threadDef
        if not lstChanged: return
        while lstChanged:
            threadId = lstChanged.pop()
#             if threadId.endswith('_lnk') and threadId.startswith('media'): continue 
            if self.treeview.exists(threadId): 
                self.delete(threadId)
            else:
                parentId, sep, threadId = threadId.rpartition('.') 
                self.registerTreeNodes(threadId)
                self.treeItemExpand(parentId, absFlag = True, flag = True)
        self.setSelection(activeThread, absFlag = False)
#         self.parseTree.setSelection(parseKnotId, absFlag = False)
        

    
    def getAbsoluteId(self, threadId, absFlag = True):
        return threadId if absFlag else self.xbmcThread.getDotPath(threadId)
    
    def registerTreeNodes(self, threadId = 'media'):
        threadKnots = self.xbmcThread.getSameTypeNodes(threadId)
        itemId = self.getAbsoluteId(self.xbmcThread.threadDef, absFlag = False)
        leaves = [itemId]
        for elem in threadKnots:
            if elem.endswith('_lnk') and not self.xbmcThread.getThreadParam(elem, 'source'): continue
            itemId = self.getAbsoluteId(elem, absFlag = False)
            itemParams = [itemId, {}]
            itemParams[1]['name'] = elem
            leaves.append(itemParams)
    
        for elem in leaves[1:]:
            self.registerNode(elem[0], childName = True)
            for dKey, dValue in elem[1].items():
                self.treeview.set(elem[0], column = dKey, value = dValue)
    
        selItem = leaves[0]
        if self.treeview.exists(selItem):
            while selItem.rpartition('.')[1]:
                self.treeview.item(selItem.rpartition('.')[0], open = True )
                selItem = selItem.rpartition('.')[0]
            self.treeview.selection_set(leaves[0])
            self.treeview.focus(leaves[0])

    def registerNode(self, iid, childName = False, absFlag = True):
        iid = self.getAbsoluteId(iid, absFlag)
        if self.treeview.exists(iid): return
        iidPart = iid.rpartition('.')
        if len(iidPart[1]) and not self.treeview.exists(iidPart[0]):
            self.registerNode(iidPart[0], childName)
        self.treeview.insert(iidPart[0], 'end',iid)
        if childName:
            self.treeview.item(iid, text = iidPart[2])
        
    def treeItemExpand(self, threadId, absFlag = True, flag = True):
        itemId = self.getAbsoluteId(threadId, absFlag)
        self.treeview.item(itemId, open = flag )  
        
    def delete(self, *items):
        items = [thread for thread in items if self.treeview.exists(thread)]
        if items: self.treeview.delete(*items)   
        
    def setSelection(self, threadId, absFlag = True):
        iid = self.getAbsoluteId(threadId, absFlag)
        self.setActualKnot()        
        self.treeview.focus(iid)
        self.treeview.selection_set(iid)

class EditTransaction(tkSimpleDialog.Dialog):

    def __init__(self, master, xbmcMenu):
        self.xbmcMenu = xbmcMenu
        self.index = xbmcMenu.threadDef
        self.setFocus = None
        self.tr = tk.StringVar()
        self.tr.trace('w', self.setDlgVars)

        self.comVar = {}
        self.keyNames = ['name', 'up']
        if xbmcMenu.getThreadAttr(xbmcMenu.threadDef, 'type') == 'thread':
            self.keyNames.extend(['url', 'regexp', 'compflags', 'nextregexp']) 
        for key in self.keyNames:
            self.comVar[key] = tk.StringVar()
        return tkSimpleDialog.Dialog.__init__(self, master, 'Edit Parse Knot')
        
    def setDlgVars(self, *args, **kwargs):
        threadId = self.tr.get()
        kType = self.xbmcMenu.getThreadAttr(self.xbmcMenu.threadDef, 'type')
        if kType == 'thread':
            params = self.xbmcMenu.getThreadAttr(threadId,'params')
            for key in self.keyNames:
                if params.get(key,None): 
                    self.comVar[key].set(params[key])
                else:
                    self.comVar[key].set('')
        self.comVar['name'].set(self.xbmcMenu.getThreadAttr(threadId,'name'))
        if self.xbmcMenu.getThreadAttr(threadId,'up'):
            self.comVar['up'].set(self.xbmcMenu.getThreadAttr(threadId,'up'))

    def body(self, master):
        master.config(relief=tk.GROOVE, bd=4)
        self.tr.set(self.index)
        kType = self.xbmcMenu.getThreadAttr(self.xbmcMenu.threadDef, 'type')
        if self.tr:
            lista = self.xbmcMenu.listKnots(knothType = kType)
            listKnots = ttk.Combobox(master, textvariable=self.tr)
            listKnots['values'] = tuple(sorted(lista))
            listKnots.configure(width=45)
            listKnots.pack(side=tk.TOP, pady=10)

        self.topGrid = tk.Frame(master)
        self.topGrid.pack(side=tk.TOP, padx=10, pady=10)
        self.topGrid.grid_columnconfigure(0, pad=20)
        
        for pos, key in enumerate(self.keyNames):
            if key == 'up': continue
            tk.Label(self.topGrid, text=key).grid(column=0, row=pos)
            ce = tk.Entry(self.topGrid, textvariable=self.comVar[key], width=45)
            ce.grid(column=1, row=pos)
            
        # Send Output To:
        texto = 'Send Output To:' if kType == 'thread' else 'Get Input From:' 
        pos = len(self.keyNames) + 2
        tk.Label(self.topGrid, text=texto).grid(column=0, row=pos)
        listKnots = ttk.Combobox(self.topGrid, textvariable=self.comVar['up'])        
        listKnots.configure(width=45)
        listKnots.grid(column=1, row=pos)

        lista = self.xbmcMenu.listKnots(knothType = kType)
        listKnots['values'] = tuple(sorted(lista))


    def apply(self):
        if self.tr.get() == self.comVar['up'].get(): return
        threadId = self.tr.get()
        for key in self.keyNames:
            if key == 'up': continue
            if self.xbmcMenu.getThreadAttr(threadId, key):
                self.xbmcMenu.parseThreads[threadId][key] = self.comVar[key].get()
            else:
                params = self.xbmcMenu.getThreadAttr(threadId, 'params')
                params[key] = self.comVar[key].get()
        if  self.comVar['up'].get() != self.xbmcMenu.getThreadAttr(threadId, 'up'):
            kType = self.xbmcMenu.getThreadAttr(threadId, 'type')
            toThread = self.comVar['up'].get()
            threadIn = (toThread, threadId) if kType == 'list' else (threadId, toThread)
            self.result = [self.xbmcMenu.getDotPath(threadId)]
            self.xbmcMenu.setNextThread(*threadIn)
            self.result.append(self.xbmcMenu.getDotPath(threadId))
        parseThread = self.xbmcMenu.parseThreads[threadId]
        for key in parseThread.keys():
            if parseThread[key] == '': parseThread.pop(key)
        params = self.xbmcMenu.getThreadAttr(threadId, 'params')
        for key in params.keys():
            if params[key] == '': params.pop(key)
        self.xbmcMenu.threadDef = threadId

class ParseThreads(tk.Toplevel):
    def __init__(self, xbmcMenu):
        tk.Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.setGUI(xbmcMenu)

    def Close(self):
        self.destroy()

    def setGUI(self, xbmcMenu):
        frame = tk.Frame(self)
        frame.pack(fill = tk.BOTH, expand = 1)
        
        uno = tk.StringVar()
        uno.set('Este es el campo 1')
        dos = tk.StringVar()
        dos.set('Segundo mensaje')
        tres = tk.StringVar()
        tres.set('No hay dos sin tres')
        self.statusBar = StatusBar(frame,[('uno: ', uno),
                                    ('dos: ', dos),
                                    ('tres: ', tres)
                                    ])
        self.statusBar.pack(side = tk.BOTTOM, fill = tk.X, expand = 1)
        
        options = (('Lumberjack-%s' % x) for  x in range(20))  # or map/lambda, [...]
        
        m1 = tk.PanedWindow(frame, sashrelief = tk.SUNKEN, bd = 10)
        m1.pack(side = tk.TOP, fill=tk.BOTH, expand=tk.YES)
#         self.leftPane = RegexpFrame(m1)
        self.leftPane = ScrolledList(m1, None) 
        self.leftPane.pack(fill = tk.X, expand=tk.YES)
        self.leftPaneFlag = True
        m1.add(self.leftPane)
        self.button = tk.Button(m1, text = "Run", command = self.toggleLeftPane)
        m1.add(self.button)
        self.m1 = m1
        self.xbmcMenu = xbmcMenu
        
        

    def toggleLeftPane(self, *args, **kwargs):
        self.m1.forget(self.leftPane)
        if not self.leftPaneFlag:
            self.m1.paneconfigure(self.leftPane, before = self.button )
        self.leftPaneFlag = not self.leftPaneFlag

if __name__ == "__main__":
    
    xbmcMenu = menuThreads.menuThreads()
    xbmcMenu.createThread('list', 'rootMenu', 'rootmenu')
    xbmcMenu.createThread('thread', 'Ultimos Cap�tulos', 'lchapter', params = {'url':'http://www.seriales.us', 'regexp':'<li><a href=\"([#].+?)\" title=\".+?\">(.+?)</a>'})
    xbmcMenu.createThread('thread', 'Ultimas Series Agregadas', 'lseries', params = {'url':'http://www.seriales.us', 'regexp':'<div class=\"bl\"> <a href=\"(.+?)\" title=\"(.+?)\">'})
    xbmcMenu.createThread('thread', 'Genero', 'genero', params = {'url':'http://www.seriales.us', 'regexp':'^<li><a href=\"(.+?)\" class=\"let\">(.+?)</a></li>', 'compflags':'re.MULTILINE'})
    xbmcMenu.createThread('thread', 'Lista Completa de Series', 'all', params = {'url':'http://www.seriales.us', 'regexp':'<li class=\".+?\"><a href=\"(.+?)\" title=\".+?\">(.+?)</a>'})    
    xbmcMenu.createThread('thread', 'A-Z', 'a_z', params = {'url':'http://www.seriales.us', 'regexp': '<li><a href=\"(.+?)\" class=\"let\">[#A-Z]</a></li>'})
    xbmcMenu.createThread('thread', 'Buscar', 'buscar', params = {'url':'http://www.seriales.us'})
    xbmcMenu.createThread('thread', 'Temporadas', 'temporadas', params = {'regexp' : '<div class=\"bl\"> <a href=\"(.+?)\" title=\"(.+?)\">'})
    xbmcMenu.createThread('thread', 'Cap�tulos', 'capitulos', params = {'regexp' : "<li class=\'lcc\'><a href=\'(.+?)\' class=\'lcc\'>(.+?)</a>"})
    xbmcMenu.createThread('thread', 'Resolvers', 'resolvers', params = {'regexp' : '<li><a href=\"([#].+?)\" title=\".+?\">(.+?)</a>'})
    xbmcMenu.createThread('thread', 'Media', 'media')
    
    xbmcMenu.setNextThread('all', 'temporadas')
    xbmcMenu.setNextThread('temporadas', 'capitulos')
    xbmcMenu.setNextThread('capitulos', 'resolvers')
    xbmcMenu.setNextThread('resolvers', 'media')
  
    xbmcMenu.setNextThread('lseries', 'capitulos')
    xbmcMenu.setNextThread('lchapter', 'resolvers')
    xbmcMenu.setNextThread('genero', 'temporadas')
    xbmcMenu.setNextThread('a_z', 'temporadas')
    xbmcMenu.setNextThread('buscar', 'temporadas')
    
    
    Root = tk.Tk()
    Root.withdraw()
    ParseThreads(xbmcMenu)
    Root.mainloop()

