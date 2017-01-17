# -*- coding: utf-8 -*-
'''
Created on 29/06/2014

@author: Alex Montes Barrios
'''
import Tkinter as tk
import json
import os
import re
import sys
import time
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
import urllib

from PIL import Image, ImageTk

import CustomRegEx
import FileGenerator
import KodiFrontEnd
import SintaxEditor
import addonSettCtrls
import collapsingFrame
import formDetector
import imageProcessor as imgp
import menuThreads
import resolverTools
import teleresolvers
import treeExplorer
import xmlFileWrapper
from OptionsWnd import AppSettingDialog
from ParseThreads import RegexpFrame, EditTransaction, StatusBar, addonFilesViewer


class XbmcAddonIDE(tk.Toplevel):

    def __init__(self, theGlobals = None):
        tk.Toplevel.__init__(self)
        self.fileHistory = []
        self.ideServer = None
        self.ideSettings = xmlFileWrapper.xmlFileWrapper('IDE_Settings.xml', hasNonDefaultFile=True)
        self.processModIdeSettings(['appdir_importer', 'var_fileHistory'])

        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.activeViewIndx = tk.StringVar()
        self.leftPaneIndx = tk.IntVar(value = -1)
        self.leftPaneVisible = tk.BooleanVar()
        self.viewBarVisible = tk.BooleanVar()
        self.viewBarVisible.set(True)
        self.rightPaneIndx = tk.IntVar(value = -1)

        self.activeViewIndx.trace("w", self.setActiveView)
        self.leftPaneVisible.trace("w", self.setLeftPaneVisibility)
        self.viewBarVisible.trace("w", self.setViewBarVisibility)

        self.xbmcThreads = menuThreads.menuThreads()
        self.addonSettings = xmlFileWrapper.xmlFileWrapper('Addon_Settings.xml')
        self.addonSettings.getParam()
        self.vrtDisc = FileGenerator.vrtDisk(self.xbmcThreads, self.addonSettings)
        self.vrtDisc.setChangeMngr(self.setSaveFlag)
        self.coder = self.vrtDisc.getApiGenerator()
        self.settings = {}

        self.setGUI()
        self.newFile()
        self.state("zoomed")
        self.iconbitmap(os.path.abspath(r'.\images\KodiIDE_icon.ico'))
        
    def checkSaveFlag(self):
        fileName = self.title()
        if fileName.endswith('**'):
            fileName = os.path.basename(self.currentFile) if not self.currentFile else 'default.pck'
            ans = tkMessageBox.askyesno('Warning', 'Do you want to save the changes you made to ' + fileName)
            if ans: self.saveFile()
            else: self.setSaveFlag(False)

    def Close(self):
        self.checkSaveFlag()
        self.ideServer.shutdown()
        self.ideServer.server_close()
        self.destroy()
        pass

    def setGUI(self):
        iconImage = imgp.getFontAwesomeIcon
        commOptions = dict(size=20,isPhotoImage=True, color='black')

        frame = tk.Frame(self)
        frame.pack(fill = tk.BOTH, expand = 1)

        ''' Se construye la barra de menus'''
        menuFrame = tk.Frame(frame, padx=4, pady=4, bg='light sea green')
        menuFrame.pack(side=tk.TOP, fill = tk.X)
        self.menuBarFrame = menuBarFrame = tk.Frame(menuFrame)
        self.menuBar = {}

        sections = [('general', ('File', 'View')),
                    ('design', ('Edit', 'Get','Tools')),
                    ('code', ('Coding', )),
                    ('addon explorer', ('Coding', ))]

        for secName, menuOp in sections:
            secName = secName.lower().replace(' ', '_')
            menuSection = tk.Frame(menuBarFrame, name=secName)
            menuSection.pack(side=tk.LEFT)
            for elem in menuOp:
                name = secName + '_' + elem.lower()
                menubutton = tk.Menubutton(menuSection, text=elem, name=name)
                menubutton.pack(side=tk.LEFT)
                self.menuBar[name] = tk.Menu(menubutton, tearoff=False)

        commOptions.update([('color', 'PaleGreen1')])
        self.menuIcon = menuIcon = iconImage('fa-navicon', **commOptions)

        self.viewPaneOp = viewPane = tk.Frame(menuFrame)
        viewPane.pack(side = tk.TOP, fill = tk.X)
        name = 'nav_menu'
        menubutton = tk.Menubutton(viewPane, image=menuIcon, text='navmenu', name=name)
        menubutton.pack(side=tk.LEFT)
        self.menuBar[name] = master = tk.Menu(menubutton, tearoff=False)
        menubutton['menu'] = self.menuBar[name]
        tk.Label(viewPane, text="The Views: ").pack(side=tk.LEFT)
        for mlabel in ['edit', 'get', 'tools', 'code']:
            menuLabel = name + '_' + mlabel
            self.menuBar[menuLabel] = tk.Menu(master, tearoff = False)

        '''Status bar'''
        self.activeKnot = tk.StringVar()
        self.addonId = tk.StringVar()
        self.message = tk.StringVar()
        self.statusBar = StatusBar(frame,[('AddonId: ', self.addonId),
                                          ('ActiveNode ', self.activeKnot),
                                          ('Selection: ', self.message)])
        self.statusBar.pack(side = tk.BOTTOM, fill = tk.X, expand = 0)

        '''Side buttons'''
        sideButtFrame = tk.Frame(frame, bg='light sea green')
        sideButtFrame.pack(side=tk.LEFT, fill=tk.Y)

        self.newIcon = newIcon = iconImage('fa-file-o', **commOptions)
        self.openIcon = openIcon = iconImage('fa-folder-open-o', **commOptions)
        self.saveIcon = saveIcon = iconImage('fa-save', **commOptions)

        tk.Button(sideButtFrame, image=newIcon, command=self.newFile).pack(side=tk.TOP)
        tk.Button(sideButtFrame, image=openIcon, command=self.__openFile).pack(side=tk.TOP)
        tk.Button(sideButtFrame, image=saveIcon, command=self.saveFile).pack(side=tk.TOP)

        self.designTabFrame = designTabFrame = tk.Frame(sideButtFrame)
        designTabFrame.pack()

        self.designTab = designTag = tk.StringVar()
        for tab in ['Api', 'Code', 'Data', 'Preview']:
            btext = '\n'.join(list(tab))
            if tab == 'Api': tab = 'Design'
            button = tk.Radiobutton(designTabFrame, width=3, value = tab, text=btext, indicatoron=0, variable=designTag)
            button.pack(side=tk.TOP)
        self.designTab.set('Design')
        self.designTab.trace("w", self.processDesignTab)

        
        '''Middle Zone'''
        m1 = collapsingFrame.collapsingFrame(frame, tk.VERTICAL, inisplit = 0.8,buttConf = 'mR')
        m1.pack(side = tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.vPaneWindow = m1

        self.setUpPaneCtrls()        

        for elem in ['Settings', 'Design', 'Addon Explorer', 'Test']:
            boton = tk.Radiobutton(viewPane, value=elem, text = elem, width = 15, variable = self.activeViewIndx, indicatoron = 0)
            boton.pack(side = tk.LEFT)

        ''' Setting the views'''
        self.activeViewIndx.set('Design')

        self.menuBuilder()

        for secName, menuOp in sections:
            secName = secName.lower().replace(' ', '_')
            menuSection = menuBarFrame.children[secName]
            for elem in menuOp:
                name = secName + '_' + elem.lower()
                menubutton = menuSection.children[name]
                menubutton.config(menu=self.menuBar[name])

    def setUpPaneCtrls(self):
        m1 = self.vPaneWindow.scndWidget
        self.parseTree = treeExplorer.ApiTree(m1, self.xbmcThreads)
        self.explorerTree = treeExplorer.treeExplorer(m1, self.vrtDisc)
        self.addonCtrlSett = addonSettCtrls.vertRadioMenu(master = m1)
        self.leftPnNames = ['parsetree', 'esplorertree']
        self.avLeftPanes = [self.parseTree, self.explorerTree, self.addonCtrlSett]

        m1 = self.vPaneWindow.frstWidget
        self.addonFilesViewer = addonFilesViewer(m1)
        self.regexpEd = RegexpFrame(m1, self.xbmcThreads, self.message)
        self.codeFrame = SintaxEditor.CodeEditor(m1, self.vrtDisc)
        xbmcFileW = xmlFileWrapper.threadXmlFileWrapper('NodeSettingFile.xml', self.xbmcThreads)
        self.NodeFrame = xmlFileWrapper.settingsDisplay(master = m1, xmlFileW = xbmcFileW)
        self.settingsPane = xmlFileWrapper.settingsDisplay(master = m1, xmlFileW = self.addonSettings)
        self.kodiFrontEnd = KodiFrontEnd.KodiFrontEnd(m1, self.server_address, self.vrtDisc)
        self.testFrame = KodiFrontEnd.ScrolledList(m1, self.server_address, self.vrtDisc)
        self.avRightPanes = [self.NodeFrame, self.testFrame, self.codeFrame, self.regexpEd,
                             self.addonFilesViewer, self.settingsPane, self.kodiFrontEnd]

        self.parseTree.setOnTreeSelProc(self.onTreeSel)
        self.parseTree.setPopUpMenu(self.popUpMenu)
        self.addonFilesViewer.setHyperlinkManager(self.hyperLinkProcessor)
        self.explorerTree.setEditorWidget(self.addonFilesViewer)
        self.regexpEd.setDropDownFiler(self.comboBoxFiler)
        self.regexpEd.setPopUpMenu(self.popUpWebMenu)
        self.regexpEd.linkedPane = self.parseTree
        self.NodeFrame.setNotifyChange(self.setSaveFlag)
        self.settingsPane.setNotifyChange(self.setSaveFlag)
        self.addonCtrlSett.setSettingsPane(self.settingsPane)

        self.leftPaneVisible.set(True)

        self.viewPanes = [('Design', 0, 3), ('Code', 0, 2), ('Data', 0, 0),
                          ('Preview', 0, 1), ('Addon Explorer', 1, 4),
                          ('Settings', 2, 5), ('Test', 0, 6)]

    def hyperLinkProcessor(self, texto):
        match = re.search('File "(?P<filename>[^"]+)", line (?P<lineno>[0-9]+)', texto)
        if not match:
            tkMessageBox.showinfo('Hyperlink Not Process', texto)                
        else:
            import xbmc
            fileName = match.group('filename')
            lineNo = match.group('lineno')
            rootId = self.vrtDisc.addon_id()
            m = re.search(r'/addons/([^/]+)/', fileName)
            if not m:
                return tkMessageBox.showerror('Hyperlink Not in actual addon', texto)
            npos = m.end()
            if m.group(1) != rootId:
                rootId = rootId + '/Dependencies/' + m.group(1)
            nodeId = rootId + '/' + fileName[npos:]
            if not self.explorerTree.treeview.exists(nodeId):
                return tkMessageBox.showerror('Hyperlink Not Found', texto)
            self.explorerTree.treeview.set(nodeId, column = 'inspos', value = lineNo + '.0')
            self.explorerTree.onTreeSelection(nodeId)
            self.addonFilesViewer.focus_force()

    def processDesignTab(self, *args, **kwargs):
        self.activeViewIndx.set('Design')

    def setActiveView(self, *args, **kwargs):
        activeTab = self.activeViewIndx.get()
        if activeTab != 'Design':
            self.designTabFrame.pack_forget()
        else:
            activeTab = self.designTab.get()
            self.designTabFrame.pack()
        for activeView, elem in enumerate(self.viewPanes):
            if activeTab == elem[0]: break
        self.actViewPane = activeView
        viewName, vwLeftPane, vwRightPane = self.viewPanes[activeView]

        for pane in self.viewPanes:
            pane = pane[0].lower().replace(' ', '_')
            child = self.menuBarFrame.children.get(pane)
            if not child: continue
            if pane != viewName.lower().replace(' ', '_'):
                child.pack_forget()
            else:
                child.pack(side=tk.LEFT)


        leftPaneIndx = self.leftPaneIndx.get()
        if leftPaneIndx != vwLeftPane:
            self.setLeftPane(vwLeftPane)

        refreshFlag = kwargs.get('refreshFlag', False)
        if refreshFlag  or leftPaneIndx != vwLeftPane:
            self.refreshLeftPane()

        rightPaneIndx = self.rightPaneIndx.get()
        if rightPaneIndx != vwRightPane:
            self.setRightPane(vwRightPane)

        if refreshFlag or rightPaneIndx != vwRightPane:
            self.refreshRightPane()

    def refreshLeftPane(self):
        activeview = self.actViewPane
        vwLeftPane = self.viewPanes[activeview][1]
        self.avLeftPanes[vwLeftPane].refreshPaneInfo()

    def refreshRightPane(self):
        activeview = self.actViewPane
        vwRightPane = self.viewPanes[activeview][2]
        self.avRightPanes[vwRightPane].initFrameExec(refreshFlag=True)



    def setLeftPane(self, leftPaneIndx):
        actLeftPane = int(self.leftPaneIndx.get())
        if actLeftPane != -1:
            pane = self.avLeftPanes[actLeftPane]
            pane.pack_forget()
        self.leftPaneIndx.set(leftPaneIndx)
        pane = self.avLeftPanes[leftPaneIndx]
        pane.pack(fill = tk.BOTH, expand = 1)

    def setLeftPaneVisibility(self, *args, **kwargs):
        isVisible = self.leftPaneVisible.get()
        self.vPaneWindow.clickButton(1)
        pass

    def setViewBarVisibility(self, *args, **kwargs):
        isVisible = self.viewBarVisible.get()
        if not isVisible:
            self.viewPaneOp.pack_forget()
        else:
            self.viewPaneOp.pack(side = tk.TOP, fill = tk.X)
        pass

    def setRightPane(self, rightPaneIndx):
        actRightPane = int(self.rightPaneIndx.get())
        if actRightPane != -1:
            pane = self.avRightPanes[actRightPane]
            pane.pack_forget()
        self.rightPaneIndx.set(rightPaneIndx)
        pane = self.avRightPanes[rightPaneIndx]
        pane.pack(fill = tk.BOTH, expand = 1)

    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')

    def menuBuilder(self):
            
        self.menuBar['popup'] = tk.Menu(self, tearoff=False)

        menuOpt = []
        # menuOpt.append(('cascade', 'Insert New', 0))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Set Regexp','Ctrl+G', 0, self.setRegexp))
        menuOpt.append(('command', 'Set NextRegexp','Ctrl+N', 0, self.setNextRegexp))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Rename','Ctrl+R', 0, self.renameKnot))
        menuOpt.append(('command', 'Delete','Ctrl+D', 0, self.deleteKnot))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Transform in a menu node','Ctrl+N', 0, self.makeMenuNode))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Edit','Ctrl+E', 0, self.editKnot))
        self.makeMenu('popup', menuOpt)
        
        menuOpt = []
        menuOpt.append(('command', 'New','Ctrl+O', 0, self.newFile))        
        menuOpt.append(('command', 'Open','Ctrl+O', 0, self.__openFile))        
        menuOpt.append(('command', 'Save','Ctrl+S', 0, self.saveFile))
        menuOpt.append(('command', 'Save as','Ctrl+S', 0, self.saveAsFile))        
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Export to XBMC','Ctrl+x', 0, self.onXbmcExport))
        menuOpt.append(('command', 'MakeZip File','Ctrl+M', 0, self.onMakeZipFile))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Close','Alt+Q', 0, self.Close))
        self.makeMenu('general_file', menuOpt)
        self.makeMenu('nav_menu', menuOpt)

        def fileHist():
            if not self.fileHistory: return
            D = os.path.abspath(self.ideSettings.getParam(srchSett = 'appdir_data'))
            frstIndx, lstIndx = 8,  tk.END
            self.menuBar['general_file'].delete(frstIndx, lstIndx)
            for k, filename in enumerate(self.fileHistory):
                flabel = os.path.basename(filename)
                self.menuBar['general_file'].add('command',
                                         label = '{} {:30s}'.format(k+1, flabel),
                                         command = lambda x=filename: self.__openFile(x))
            self.menuBar['general_file'].add('separator')
            self.menuBar['general_file'].add('command', label='Close',accelerator='Alt+Q', underline=0, command=self.Close)

        self.menuBar['general_file'].config(postcommand = fileHist)
        self.menuBar['nav_menu'].config(postcommand = self.navMenuPostCommand)

        menuOpt = []
        menuOpt.append(('command', 'File','Ctrl+F', 0, self.importFile))
        menuOpt.append(('command', 'Url','Ctrl+U', 0, self.importUrl))
        menuOpt.append(('command', 'Clipboard','Ctrl+L', 0, self.regexpEd.pasteFromClipboard))
        menuOpt.append(('command', 'Selected Url','Ctrl+S', 0, self.selectedURL))
        menuOpt.append(('command', 'Selected Form','Ctrl+F', 0, self.selectedForm))
        self.makeMenu('design_get', menuOpt)
        self.makeMenu('nav_menu_get', menuOpt)

        menuOpt = []
        menuOpt.append(('cascade', 'Insert New', 0))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Rename','Ctrl+R', 0, self.renameKnot))
        menuOpt.append(('command', 'Delete','Ctrl+D', 0, self.deleteKnot))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Set Url','Ctrl+U', 0, self.setUrl))
        menuOpt.append(('command', 'Set Regexp','Ctrl+R', 0, self.setRegexp))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Add Header','Ctrl+N', 0, lambda param = 'headregexp': self.setActNodeParam(param)))
        menuOpt.append(('command', 'Add Footer','Ctrl+N', 0, lambda param = 'nextregexp': self.setActNodeParam(param)))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Set Header/Footer label','Ctrl+N', 0, lambda param = 'label': self.setHeaderFooterParam(param)))
        menuOpt.append(('command', 'Set Header/Footer options','Ctrl+N', 0, lambda param = 'options': self.setHeaderFooterParam(param)))
        menuOpt.append(('command', 'Set Header/Footer selection','Ctrl+N', 0, lambda param = 'selection': self.setHeaderFooterParam(param)))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Transform in a menu node','Ctrl+N', 0, self.makeMenuNode))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Edit','Ctrl+E', 0, self.editKnot))
        self.makeMenu('nav_menu_edit', menuOpt)
        self.makeMenu('design_edit', menuOpt)
         
        menuOpt = []
        menuOpt.append(('command', 'Source','Ctrl+B', 0, self.newSendOutput))
        menuOpt.append(('command', 'Output','Ctrl+A', 0, self.newReceiveInput))
        menuOpt.append(('command', 'Link','Ctrl+A', 0, self.newLink))
        self.makeMenu('design_edit.Insert_New', menuOpt)
        self.makeMenu('nav_menu_edit.Insert_New', menuOpt)
        # menuOpt = []
        # menuOpt.append(('command', 'New','Ctrl+S', 0, self.newParseKnot))
        # menuOpt.append(('command', 'Set ActiveKnoth','Ctrl+A', 0, self.setActiveKnot))
        # self.makeMenu('Knoth', menuOpt)

        menuOpt = []
        menuOpt.append(('checkbutton', 'Toggle Left Pane View', self.leftPaneVisible,[False, True]))
        menuOpt.append(('checkbutton', 'Toggle View Bar', self.viewBarVisible,[False, True]))
        menuOpt.append(('separator',))
        self.makeMenu('general_view', menuOpt)
        def miLambda():
            frstIndx, lstIndx = 2, tk.END
            self.menuBar['View'].delete(frstIndx, lstIndx)
            if self.viewBarVisible.get(): return
            self.menuBar['View'].add('separator')
            for k, view in enumerate(self.viewPanes):
                self.menuBar['View'].add_radiobutton(label = view[0], variable = self.activeViewIndx, value = view[0])

        self.menuBar['general_view'].config(postcommand = miLambda)
                                                           
        menuOpt = []
        menuOpt.append(('command', 'Addon','Ctrl+E', 0, lambda key = '2':self.codeAddon(key)))
        menuOpt.append(('command', 'DownThread','Ctrl+D', 0, self.codeDownThread))
        menuOpt.append(('command', 'ActiveKnot','Ctrl+R', 0, self.codeActiveKnot))
        menuOpt.append(('command', 'SaveCode','Ctrl+o', 0, self.saveCode))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Reset Code','Ctrl+o', 0, self.resetCode))
        self.makeMenu('code_coding', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'SaveCode','Ctrl+o', 0, self.saveCode))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Reset Code','Ctrl+o', 0, self.resetCode))
        self.makeMenu('addon_explorer_coding', menuOpt)
        self.makeMenu('nav_menu_code', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'HTML struct','Ctrl+R', 0, self.HTMLstruct))
        menuOpt.append(('command', 'Forms','Ctrl+F', 0, self.formsDetector))
        menuOpt.append(('cascade', 'Decoders', 0))
        menuOpt.append(('cascade', 'Ofuscators', 0))
        menuOpt.append(('command', 'pretifyJS','Ctrl+P', 0, self.makeJavaScriptPretty))
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Resolve Hyperlink','Ctrl+R', 0, self.resolveHyperlink))
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Options','Ctrl+S', 0, self.programSettingDialog))
        self.makeMenu('design_tools', menuOpt)
        self.makeMenu('nav_menu_tools', menuOpt)


        # self.menuBar['design_tools.Decoders'] = tk.Menu(self, tearoff=False)

        menuOpt = []
        menuOpt.append(('command', 'Base64','', 2, lambda x='base64': self.decodeWith(x)))
        menuOpt.append(('command', 'Unquote','', 0, lambda x='unquote': self.decodeWith(x)))
        menuOpt.append(('command', 'decodeUriComponent','', 0, lambda x='decodeUriComponent': self.decodeWith(x)))
        menuOpt.append(('command', 'utf-8','', 0, lambda x='utf-8': self.decodeWith(x)))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Unpack','', 0, self.unPack))
        self.makeMenu('design_tools.Decoders', menuOpt)
        self.makeMenu('nav_menu_tools.Decoders', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'l=~[];l={ ...','', 2, lambda x='type1': self.deOfuscate(x)))
        menuOpt.append(('command', '_0x12a8=[ ...','', 0, lambda x='type2': self.deOfuscate(x)))
        self.makeMenu('design_tools.Ofuscators', menuOpt)
        self.makeMenu('nav_menu_tools.Ofuscators', menuOpt)

    def navMenuPostCommand(self):
        menuId = 'nav_menu'
        activeView = self.activeViewIndx.get()
        if activeView == 'Design': activeView = self.designTab.get()
        master = self.menuBar[menuId]
        frstIndx, lstIndx = 8,  tk.END
        master.delete(frstIndx, lstIndx)
        if activeView == 'Design':
            for mLabel in ['edit', 'get', 'tools']:
                menuLabel = menuId + '_' + mLabel
                master.add('cascade',
                               label = '{:30s}'.format(mLabel.capitalize()),
                               menu = self.menuBar[menuLabel])
            master.add('separator')
        elif activeView in ['Code', 'Addon Explorer']:
            mLabel= 'code'
            menuLabel = menuId + '_' + mLabel
            master.add('cascade',
                           label = '{:30s}'.format(mLabel.capitalize()),
                           menu = self.menuBar[menuLabel])
            master.add('separator')
        if self.fileHistory:
            for k, filename in enumerate(self.fileHistory):
                flabel = os.path.basename(filename)
                master.add('command',
                             label = '{} {:30s}'.format(k+1, flabel),
                             command = lambda x=filename: self.__openFile(x))
        master.add('separator')
        master.add('command', label='Close',accelerator='Alt+Q', underline=0, command=self.Close)



    def deOfuscate(self, tipo):
        content =  self.regexpEd.getContent()
        try:
            if tipo == 'type1':
                content = resolverTools.ofuscator1(content)
            elif tipo == 'type2':
                content = resolverTools.ofuscator2(content)
        except Exception as e:
            tkMessageBox.showerror('Deofuscator Error', e)
        else:
            self.regexpEd.setContent(content)

    def decodeWith(self, decoder):
        content =  self.regexpEd.getContent()
        try:
            if decoder == 'decodeUriComponent':
                content = urllib.unquote(content).decode('utf-8')
            elif decoder == 'unquote':
                content = resolverTools.unquote(content)
            else:
                content = content.decode(decoder)
        except Exception as e:
            tkMessageBox.showerror('Decode Error', e)
        else:
            self.regexpEd.setContent(content)

    def makeJavaScriptPretty(self):
        javaScriptCode =  self.regexpEd.getContent()
        prettyJS = teleresolvers.prettifyJS(javaScriptCode)
        self.regexpEd.setContent(prettyJS)

    def formsDetector(self):
        baseUrl = self.regexpEd.getActiveUrl()
        content = self.regexpEd.getContent()
        form_xml = formDetector.getFormXmlStr(content)
        if 'category' not in form_xml: return tkMessageBox.showinfo('Form Detector', 'No forms in url content')
        browser = AppSettingDialog(self, form_xml, isFile = False, settings = {}, title = 'Form Detector', dheight = 600, dwidth = 400)
        if browser.allSettings:
            formAttr = dict([(key[3:], value) for key, value in browser.allSettings if key.startswith('fa_')])
            formFields = browser.allSettings[len(formAttr):]
            # filterFunc = lambda x: (x[0].startswith('if_') and x[1]) or (not x[0].startswith('if_') and x[1] is not 0)
            filterFunc = lambda x: x[1] is not 0
            formFields = filter(filterFunc, formFields)
            trnValueFnc = lambda x: (x[0],formDetector.unescapeXml(x[1].partition('|')[0])) if isinstance(x[1], basestring) else (x[0], 'on')
            formFields = map(trnValueFnc, formFields)
            trnKeyFnc = lambda x: (x[0][3:], '@' + x[1]) if x[0].startswith('if_') else x
            formFields = map(trnKeyFnc, formFields)
            # formFields = [(key, trnFnc(value)) for key, value in browser.allSettings if not (key.startswith('fa_') or value == 0)]
            refererOpt = '-e ' + '"' + baseUrl + '"'
            curlCommand = formDetector.getCurlCommand(baseUrl, formAttr, formFields, refererOpt)
            # print curlCommand

            self.regexpEd.setActiveUrl(curlCommand)

    def HTMLstruct(self):
        if not self.regexpEd.isZoomed():
            return tkMessageBox.showinfo('HTML struct', 'You must zoom in to html struct')
        tagSpan = self.regexpEd.getSelRange('actMatch')
        content = self.regexpEd.getContent(*tagSpan)
        try:
            tagList = CustomRegEx.ExtRegexParser().htmlStruct(content, 0)
        except:
            equis = 'Not HTML conform'
            tkMessageBox.showinfo('Actual match HTMLstruct', equis)
        else:
            head = tagList[0]
            answer = [[head[0][0], head[1], None]]
            stackLevel = [0]
            fullIds = '\n'.join([elem[1] for elem in tagList])
            for k, elem in enumerate(tagList[1:], start=1):
                level = elem[1].count('.')
                stackLevel = stackLevel[:level]
                dadPos = stackLevel[-1]
                rawid = elem[1].rpartition('.')[2]
                id = rawid.replace('[', '\[').replace(']', '\]')
                fullIds = '\n'.join([elem[1] for elem in tagList[:k+1]])
                numId = len(re.findall(r'.+?\.%s$' % id, fullIds, re.MULTILINE))
                if numId == 1:
                    id = '.%s' % rawid
                else:
                    dadId = answer[dadPos][1]
                    id = '%s.%s' % (dadId, rawid)
                answer.append([elem[0][0], id, dadPos])
                stackLevel.append(k)
            for k in range(-1, -len(answer), -1):
                insPos = answer[k][0]
                insStr = '<!-- %s -->' % answer[k][1]
                content = content[:insPos] + insStr + content[insPos:]
            self.regexpEd.setContent(content, newUrl=False)

    def resolveHyperlink(self):
        textw = self.regexpEd.txtEditor.textw
        selRange = textw.tag_ranges('actMatch')
        if not selRange:
            tkMessageBox.showerror('Error', 'No actual match detected')
            return
        selRange = textw.tag_nextrange("hyper", *selRange)
        if not selRange:
            tkMessageBox.showerror('Error', 'No hyperlink detected')
            return
        hyperlnk = textw.get(*selRange)
        if not hyperlnk.startswith('http'):
            tkMessageBox.showerror('Error', 'Not a valid hyperlink.\n It must start with http:// or https://')
            return

        try:
            import urlresolver
        except:
            tkMessageBox.showerror('Import Error', 'Module urlresolver not available')
        else:
            try:
                media_url = urlresolver.HostedMediaFile(url=hyperlnk).resolve()
            except Exception as e:
                tkMessageBox.showerror('Urlresolver Error', e)
            else:
                if not media_url:
                    tkMessageBox.showerror('Resolver Error', 'The url %s was not possible to resolve' % hyperlnk)
                else:
                    answ = tkMessageBox.askokcancel('Hyperlink Solved', 'The hyperlink %s is solved to:\n\n%s\n\nCopy to clipboard?' % (hyperlnk,media_url))
                    if answ:
                        self.clipboard_clear()
                        self.clipboard_append(media_url)
        finally:
            pass

    def detectPacker(self):
        content = self.regexpEd.getContent()
        from jsunpack import detect
        result = detect(content)
        if result:
            tkMessageBox.showinfo('Pack content', 'The content is packed')
        else:
            tkMessageBox.showerror('Pack content', 'The content is packed')
        
    def unPack(self):
        content = self.regexpEd.getContent()
        try:
            content = resolverTools.unpack(content)
        except Exception as e:
            tkMessageBox.showerror('Unpack error', str(e))
        else:
            self.regexpEd.setContent(content, newUrl = False)
        
    def unwiseProcess(self):
        content = self.regexpEd.getContent()
        from toRecycle.unwise import unwise_process
        content = unwise_process(content)
        self.regexpEd.setContent(content, newUrl = False)

    def onMakeZipFile(self):
        D = os.path.abspath(self.ideSettings.getParam(srchSett = 'appdir_export'))
        zipFileName = tkFileDialog.asksaveasfilename(title = 'Zip File to create', initialdir=D, defaultextension='.zip', filetypes=[('Zip Files', '*.zip'), ('All Files', '*.*')])
        if zipFileName:
            if os.path.exists(zipFileName): # Si no se borra el archivo primero, tiene probleas
                os.remove(zipFileName)
            self.onXbmcExport(zipFileName)
            # Este procedimiento se hce necesario para asegurar que en el android el archivo zip no tenga problemas
            with open(zipFileName, 'r+b') as f:   
                data = f.read()  
                pos = data.find('\x50\x4b\x05\x06') # End of central directory signature  
                if (pos > 0):  
                    f.seek(pos + 22)   # size of 'ZIP end of central directory record' 
                    f.truncate()  
              
    def getAddonSettings(self, srchSett = None):
        return self.addonSettings.getParam(srchSett)

    # noinspection PyUnresolvedReferences
    def onXbmcExport(self, name = None):
        import xbmc
        addonSet = self.addonSettings
        if addonSet.isDefault('addon_id'):
            tkMessageBox.showinfo('Required Information', 'Please set the Addon Id, before this operation can be executed')
            self.activeViewIndx.set('Settings')
            return
        addon_id = addonSet.getParam('addon_id')
        baseDir = addonSet.getParam('appdir_xbmchome') or xbmc.translatePath('special://home/addons')
        if not name and os.path.exists(os.path.join(baseDir, addon_id)):
            answ = tkMessageBox.askokcancel('Xbmc Export', 'The addon with id = %s already exists.\nDo you want to replace it?'%addon_id)
            if not answ: return
        self.vrtDisc.mapVrtDisk(name)

    def programSettingDialog(self):
        nonDefParam = self.ideSettings.getNonDefaultParams()
        settingObj = AppSettingDialog(self, 'IDE_Settings.xml', settings = nonDefParam, title = 'IDE General Settings')
        self.ideSettings.setNonDefaultParams(settingObj.result)
        if settingObj.applySelected:
            self.ideSettings.save()
            self.processModIdeSettings(settingObj.applySelected)

    def setServer(self):
        host, port = map(self.ideSettings.getParam, ('server_host', 'server_port'))
        self.server_address = server_address = (host, int(port))
        if self.ideServer:
            self.ideServer.shutdown()
            self.ideServer.server_close()
        import KodiIDEServer
        self.ideServer = KodiIDEServer.runServer(server_address=server_address)

    def setIdeParams(self, ideParams):
        for key in ideParams:
            if key == 'appdir_xbmc':
                import xbmc
                xbmc.special_xbmc = '' if self.ideSettings.isDefault(key) else self.ideSettings.getParam(key)
            elif key == 'appdir_xbmchome':
                import xbmc
                xbmc.special_home = '' if self.ideSettings.isDefault(key) else self.ideSettings.getParam(key)
            elif key == 'var_fileHistory':
                self.fileHistory = json.loads(self.ideSettings.getParam(key))

    def processModIdeSettings(self, settingsIds):
        servermod = set(('server_host', 'server_port')).intersection(settingsIds)
        if servermod or 'appdir_importer' in settingsIds:
            importerPath = self.ideSettings.getParam('appdir_importer')
            importerPath = os.path.abspath(importerPath)
            sys.path.append(importerPath)
            self.setServer()
            settingsIds = self.ideSettings.keys()
        self.setIdeParams(settingsIds)

    def codeAddon(self,key):
        if self.rightPaneIndx.get() != key: return self.rightPaneIndx.set(key)
        execObj = self.xbmcThreads if key in ['0', '3'] else self.coder
        self.avRightPanes[int(key)].initFrameExec(execObj, param = True)

    def codeDownThread(self):
        if self.rightPaneIndx.get() != '2': return self.rightPaneIndx.set('2')
        threadId = self.xbmcThreads.threadDef
        self.codeFrame.setContentToNodeCode(threadId, incDownThread = True)

    def resetCode(self):
        activeView = self.actViewPane
        viewName, vwLeftPane, vwRightPane = self.viewPanes[activeView]
        if viewName != 'Code':
            tkMessageBox.showinfo('Reset Code', 'This option is available only in Code View')
            return
        nodeId =self.xbmcThreads.threadDef
        if nodeId in self.coder.modSourceCode:
            self.coder.modSourceCode.pop(nodeId)
        self.xbmcThreads.unlockThread(nodeId)
        widget = self.avRightPanes[vwRightPane]
        leftwidget = self.avLeftPanes[vwLeftPane]
        leftwidget.refreshFlag = True
        leftwidget.refreshPaneInfo()
        widget.initFrameExec()
        self.setSaveFlag(True)


    def saveCode(self):
        activeView = self.actViewPane
        viewName, vwLeftPane, vwRightPane = self.viewPanes[activeView]
        widget = self.avRightPanes[vwRightPane]
        leftwidget = self.avLeftPanes[vwLeftPane]
        if viewName not in ['Code', 'Addon Explorer']: return
        partialMod = viewName == 'Code'
        fileGenerator = self.vrtDisc.getFileGenerator()
        modSource, contType, fileId = widget.getContent()
        if contType == 'genfile':
            fileGenerator.setSource(fileId, modSource, partialMod)
            if not partialMod:
                modSource = fileGenerator.getSource(fileId)
                widget.setContent((modSource, contType, fileId), '1.0')
            else:
                widget.initFrameExec()
            self.setSaveFlag(True)
            leftwidget.refreshFlag = True
            leftwidget.refreshPaneInfo()
        if contType == 'file':
            if os.path.splitext(fileId)[1] in ['.py', '.txt', '.xml']:
                with open(fileId, 'w') as f:
                    f.write(modSource)
    
    def codeActiveKnot(self):
        if self.rightPaneIndx.get() != '2': return self.rightPaneIndx.set('2')
        threadId = self.xbmcThreads.threadDef
        self.codeFrame.setContentToNodeCode(threadId)
        
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
            elif menuType == 'radiobutton':
                menuType, radioVar, radioOps = menuDesc
                for k, elem in enumerate(radioOps):
                    master.add_radiobutton(label = elem, variable = radioVar, value = k) 
            elif menuType == 'checkbutton':
                menuType, checkLabel, checkVar, checkVals = menuDesc
                master.add_checkbutton(label=checkLabel, variable=checkVar, onvalue=checkVals[1], offvalue=checkVals[0])
            else:
                master.add('separator') 

    def makeMenuNode(self):
        knotId = self.getActiveKnot()
        if self.xbmcThreads.isthreadLocked(knotId):
            return tkMessageBox.showerror('Access Error', knotId + ' is a Code locked Node')
        parseKnotId = tkSimpleDialog.askstring('Create Menu Node', 'Menu ID to create:')
        if not parseKnotId:return
        lstChanged = []
        self.xbmcThreads.createThread('list', parseKnotId, parseKnotId)
        menuThread = self.xbmcThreads.threadDef
        url = self.xbmcThreads.getThreadParam(menuThread, 'url')
        regexp = self.xbmcThreads.getThreadParam(menuThread, 'regexp')
        compflags = eval(self.xbmcThreads.getThreadParam(menuThread, 'compflags'))
        submenus = self.testFrame.parseUrlContent(url, regexp, compflags)
        for k, elem in enumerate(submenus):
            menuName = elem['label']
            menuId = 'opc{:0>2d}_{:}'.format(k,menuThread.replace(' ', '_'))
            self.xbmcThreads.createThread('list', menuName, menuId)
            self.xbmcThreads.setNextThread(parseKnotId, menuId)
            self.xbmcThreads.setThreadParams(menuId, {'option':k})
            self.xbmcThreads.setNextThread(menuId, menuThread)
            lstChanged.append(menuThread + '_' + menuId + '_' + 'lnk')
        lstChanged = map(self.xbmcThreads.getDotPath, lstChanged)
        self.parseTree.refreshTreeInfo(parseKnotId, lstChanged = lstChanged)
        if lstChanged: self.setSaveFlag(True)

    def editKnot(self):
        knotId = self.getActiveKnot()
        if not knotId: return -1
        if self.xbmcThreads.isthreadLocked(knotId):
            return tkMessageBox.showerror('Access Error', knotId + ' is a Code locked Node')
        editDlg = EditTransaction(self, self.xbmcThreads)
        if editDlg.result: self.setSaveFlag(True)
        self.parseTree.refreshTreeInfo(lstChanged = editDlg.result)

    def getActiveKnot(self):
        return self.xbmcThreads.threadDef
    
    def initRightPane(self, param = False):
        viewTy = int(self.rightPaneIndx.get())
#         execObj = self.xbmcThreads if viewTy in [0,3] else self.coder
        self.avRightPanes[viewTy].initFrameExec(refreshFlag=param)
            
    def setActiveKnot(self, activeKnotId = None):
        if not activeKnotId:
            activeKnotId = tkSimpleDialog.askstring('Set ActiveKnot', 'Enter the new ActiveKnot:')
        # if activeKnotId and self.xbmcThreads.getThreadAttr(activeKnotId, 'name') != -1:
        if activeKnotId and not activeKnotId.endswith('_lnk'):
            self.xbmcThreads.threadDef = activeKnotId
            self.initRightPane(param = False)
            self.parseTree.setSelection(activeKnotId, absFlag = False)
                
    def onTreeSel(self, node = None):
        treeview = self.parseTree.treeview
        iid = treeview.focus()
        parent, sep, threadId = iid.rpartition('.')
        if self.xbmcThreads.getThreadAttr(threadId, 'type') == 'link':
            treeview.update()
        else:
            self.setActiveKnot(threadId)
            self.activeKnot.set(threadId)
        
    def comboBoxFiler(self):
        nodeLst = [elem for elem in self.xbmcThreads.getSameTypeNodes('media') if not elem.endswith('_lnk')]
        getRegEx = self.xbmcThreads.getThreadParam
        getParent = lambda x: '(?#<rexp-' + self.xbmcThreads.getParent(x) + '>)' if self.xbmcThreads.getParent(x) else None
        lista = [ ['(?#<rexp-%s>)' % node , getRegEx(node, 'regexp'), getParent(node)] for node in nodeLst]
        headLst = lambda node, header_footer: [elem.split('<->') for elem in getRegEx(node, header_footer).split('<=>')]
        for node in nodeLst:
            if not getRegEx(node, 'nextregexp'): continue
            headers = headLst(node, 'nextregexp')
            for k in range(len(headers)):
                if len(headers[k]) == 1 and headers[k][0].find('<->') == -1:
                    headers[k] = ['footvar%s' % (k + 1), '|' + headers[k][0]]
                elif len(headers[k]) == 2 and headers[k][1].find('|') == -1:
                    headers[k] = [headers[k][0], '|' + headers[k][1]]
            lista.extend([['(?#<rfoot-%s-%s>)' % (node, label), regexp.split('|')[1], '(?#<rexp-%s>)' % node] for label, regexp in headers])
            lista.extend([['(?#<rfoot-%s-%s-sel>)' % (node, label), regexp.split('|')[0], '(?#<rexp-%s>)' % node] for label, regexp in headers if regexp.split('|')[0]])

        for node in nodeLst:
            if not getRegEx(node, 'headregexp'): continue
            headers = headLst(node, 'headregexp')
            lista.extend([['(?#<rhead-%s-%s>)' % (node, label), regexp.split('|')[1], '(?#<rexp-%s>)' % node] for label, regexp in headers])
            lista.extend([['(?#<rhead-%s-%s-sel>)' % (node, label), regexp.split('|')[0], '(?#<rexp-%s>)' % node] for label, regexp in headers if regexp.split('|')[0]])
        return sorted(lista)
        
    def popUpMenu(self):
        popUpMenu = self.menuBar['design_edit']
        treeview = self.parseTree.treeview
        iid = treeview.focus()
        menuState = tk.DISABLED if iid == 'media' else tk.NORMAL 
        self.menuBar['design_edit.Insert_New'].entryconfigure(1, state= menuState)
        return popUpMenu
    
    def popUpWebMenu(self):
        return self.menuBar['design_tools.Decoders']

    def setKnotParam(self, paramStr, paramValue):
        if not self.getActiveKnot(): return -1
        knotId = self.getActiveKnot()
        if paramStr not in ['url', 'regexp'] and self.xbmcThreads.isthreadLocked(knotId):
            tkMessageBox.showerror('Access Error', knotId + ' is a Code locked Node')
            return 'locked'
        params = self.xbmcThreads.getThreadAttr(knotId, 'params')
        params[paramStr] = paramValue
        self.setSaveFlag(True)

    def setHeaderFooterParam(self, param):
        knotId = self.getActiveKnot()
        hdrFtr = []
        regExp = self.xbmcThreads.getThreadParam(knotId, 'nextregexp') or ''
        nHeader = 0
        if regExp:
            hdrFtr.extend([elem.split('<->') for elem in regExp.split('<=>')])
            nHeader = len(hdrFtr)
        regExp = self.xbmcThreads.getThreadParam(knotId, 'headregexp') or ''
        if regExp: hdrFtr.extend([elem.split('<->') for elem in regExp.split('<=>')])
        if not hdrFtr:
            tkMessageBox.showinfo('Header/Footer edit',
                                  "The active node doesn't have any header or Footer.\n"
                                  "Please add a header or footer before")
        else:
            msg = 'Please imput the number identifying the header or footer to edit:\n'
            msg += '\n'.join(['%s %s %s' % (k, 'footer' if k < nHeader else 'header', elem[0]) for k, elem in enumerate(hdrFtr)])
            nItem = tkSimpleDialog.askinteger('Header/Footer edit', msg)
            if not nItem: return
            nItem = max(0, min(nItem, len(hdrFtr)))
            rtype = 'rfoot' if nItem < nHeader else 'rhead'
            cbLabel = '(?#<%s-%s-%s>)' % (rtype, knotId, hdrFtr[nItem][0])
            if param == 'label':
                lblStr = tkSimpleDialog.askstring('Header/Footer Edition', 'Input new label for header/footer No. %s' % nItem)
                hdrFtr[nItem][0] = lblStr or hdrFtr[nItem][0]
            else:
                if hdrFtr[nItem][1].find('|') == -1: hdrFtr[nItem][1] = '|' + hdrFtr[nItem][1]
                sel, opts = hdrFtr[nItem][1].split('|', 1)
                if param == 'selection':
                    sel = self.regexpEd.getRegexpPattern()
                    cbLabel = cbLabel[:-2] + '-sel>)'
                else: opts = self.regexpEd.getRegexpPattern()
                hdrFtr[nItem][1] = sel + '|' + opts
            if nItem < nHeader:
                hdrFtr = '<=>'.join([label + '<->' + expr for label, expr in hdrFtr[:nHeader]])
                varName = 'nextregexp'
            else:
                hdrFtr = '<=>'.join([label + '<->' + expr for label, expr in hdrFtr[nHeader:]])
                varName = 'headregexp'
            self.setKnotParam(varName, hdrFtr)
            if param != 'label':
                self.regexpEd.regexpFrame.cbIndex.set(cbLabel)
            else:
                tkMessageBox.showinfo('Header/Footer Edition', 'Label set succesfully')

    def setActNodeParam(self, param):
        if param == 'url':
            self.setKnotParam('url', self.regexpEd.getActiveUrl())
        elif param in ('headregexp', 'nextregexp'):
            knotId = self.getActiveKnot()
            regExp = self.xbmcThreads.getThreadParam(knotId, param) or ''
            nItem = 1 + (regExp.count('<=>') + 1) if regExp else 0
            varName = 'labelvar%s' % nItem if param != 'nextregexp' or nItem > 1 else 'Next>>>'
            prefix = ('<=>' if regExp else '') + '%s<->|' % varName
            regExp += prefix + self.regexpEd.getRegexpPattern(withFlags=True)
            self.setKnotParam(param, regExp)

            cbLabel = '(?#<rhead-%s-%s>)' if param == 'headregexp' else '(?#<rfoot-%s-%s>)'
            cbLabel = cbLabel % (knotId, varName)
            self.regexpEd.regexpFrame.cbIndex.set(cbLabel)
                
    def setUrl(self):
        self.setKnotParam('url', self.regexpEd.getActiveUrl())
        actKnot = self.xbmcThreads.threadDef
        getThParam = self.xbmcThreads.getThreadParam
        actState = (getThParam(actKnot, 'url'), getThParam(actKnot, 'regexp'))

        
    def setNextRegexp(self):
        self.setKnotParam('nextregexp', self.regexpEd.getRegexpPattern())
        
    def setRegexp(self):
        exitFlag = self.setKnotParam('regexp', self.regexpEd.getRegexpPattern())
        if exitFlag == 'locked': return
        # self.setKnotParam('compflags', self.regexpEd.getCompFlags())
        self.regexpEd.regexBar.cbIndex.set('(?#<rexp-' + self.getActiveKnot() + '>)')
        actKnot = self.xbmcThreads.threadDef
        getThParam = self.xbmcThreads.getThreadParam
        actState = (getThParam(actKnot, 'url'), getThParam(actKnot, 'regexp'))

        
    def newSendOutput(self):
        refKnot = self.xbmcThreads.threadDef
        self.newParseKnot(refKnot, outputToRefKnoth = True)
        
    def newLink(self):
        xmlStr = ['<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
                  '<settings>',
                  '<category label="Settings">',
                  '<setting id="lnk_from" type="text" label="From:   " default="" enable="false"/>',
                  '<setting id="lnk_to" type="text" label="To:   " default=""/>',
                  '<setting id="lnk_discrim_prefix" type="labelenum" label="Discrim Prefix:   " enable="true" default="0" values="option|optlabel|optnumber|urldata|urlin|urljoin|urlout"/>',
                  '<setting id="lnk_discrim_suffix" type="text" eneble="true" label="Discrim Suffix:   " default=""/>',
                  '<setting id="lnk_discrim_value" type="text" label ="Discrim Value: " default="1"/>',
                  '</category>',
                  '</settings>'
                  ]
        xbmcThreads = self.xbmcThreads
        threadDef = xbmcThreads.threadDef
        tipo = xbmcThreads.getThreadAttr(threadDef, 'type')
        if tipo == 'list':
            parseKnotId = tkSimpleDialog.askstring('Create Link', 'ParseKnot ID to link:')
            result = {}
        elif tipo == 'thread':
            discrim = xbmcThreads.getThreadParam(threadDef, 'discrim')
            nonDefParam = {'lnk_from':threadDef}
            if discrim:
                discrimprefix, discrimsuffix = re.search(r'([a-z]+)([0-9]+)*', discrim).groups()
                nonDefParam['lnk_discrim_prefix'] = discrimprefix
                if discrimsuffix: nonDefParam['lnk_discrim_suffix'] = discrimsuffix
                xmlStr[5] = '<setting id="lnk_discrim_prefix" type="text" enable="false" label="Discrim Prefix:   " default=""/>'
                xmlStr[6] = '<setting id="lnk_discrim_suffix" type="text" enable="false" label="Discrim Suffix:   " default=""/>'
            xmlStr = '\n'.join(xmlStr)
            dialogObj = AppSettingDialog(self, xmlStr, isFile = False, settings = nonDefParam, title = 'New Link')
            if not dialogObj.applySelected and dialogObj.result['lnk_to']: return
            result = dialogObj.result
            parseKnotId = dialogObj.result['lnk_to']
        if parseKnotId:
            self.xbmcThreads.setLinkTie(self.xbmcThreads.threadDef, parseKnotId)
            if result:
                discrim = result['lnk_discrim_prefix'].split('|', 1)[0]
                discrim += result.get('lnk_discrim_suffix', '')
                params = xbmcThreads.getThreadAttr(threadDef, 'params')
                params['discrim'] = discrim
                xbmcThreads.setThreadParams(threadDef, params)
                lnkTo = result['lnk_to']
                discrimValue = result.get('lnk_discrim_value', '')
                params = xbmcThreads.getThreadAttr(lnkTo, 'params')
                params[discrim] = discrimValue
                xbmcThreads.setThreadParams(lnkTo, params)
            lnkNode = parseKnotId + '_' + self.xbmcThreads.threadDef +'_lnk'
            lstChanged = [self.xbmcThreads.getDotPath(lnkNode)]
            self.parseTree.refreshTreeInfo(self.xbmcThreads.threadDef, lstChanged = lstChanged)
            self.refreshRightPane()
            self.setSaveFlag(True)

    def newReceiveInput(self):
        refKnot = self.xbmcThreads.threadDef
        self.newParseKnot(refKnot, outputToRefKnoth = False)
        
    def deleteKnot(self, threadId = None):
        if not threadId:
            iid = self.parseTree.treeview.focus()
            iid = iid.rpartition('.')[2]
            if self.xbmcThreads.getThreadAttr(iid, 'type') == 'link':
                threadId = iid
            else:
                threadId = self.xbmcThreads.threadDef
        lstChanged = [self.xbmcThreads.getDotPath(threadId)]
        if self.xbmcThreads.getThreadAttr(threadId, 'type') == 'thread':
            for lnkId in self.xbmcThreads.getLinks(threadId):
                if self.xbmcThreads.getThreadParam(lnkId, 'source'):continue
                toNode = self.xbmcThreads.getThreadAttr(lnkId, 'name')
                fromNode = self.xbmcThreads.getThreadAttr(lnkId, 'up')
                lnkRev = self.xbmcThreads.getLinkId(fromNode, toNode)
                lstChanged.append(self.xbmcThreads.getDotPath(lnkRev))
        lista = [elem for elem in self.xbmcThreads.getSameTypeNodes(threadId) if not elem.endswith('_lnk')]
        self.xbmcThreads.deleteNode(threadId)
        if lstChanged: self.setSaveFlag(True)
        self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
        self.coder.modifyCode('delete', *lista)
        self.onTreeSel()


    def renameKnot(self, threadId = None):
        if not threadId: threadId = self.xbmcThreads.threadDef
        if self.xbmcThreads.isthreadLocked(threadId):
            return tkMessageBox.showerror('Access Error', threadId + ' is a Code locked Node')
        newKnotId = tkSimpleDialog.askstring('Create new ParseKnotID', 'New ParseKnot ID to rename:')
        lstChanged = [self.xbmcThreads.getDotPath(threadId)]
        self.xbmcThreads.rename(threadId, newKnotId)
        lstChanged.append(self.xbmcThreads.getDotPath(newKnotId))
        self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
        self.coder.modifyCode('rename', threadId, newKnotId)
        if lstChanged: self.setSaveFlag(True)
        
    def newParseKnot(self, refKnot = None, outputToRefKnoth = True):
        parseKnotId = tkSimpleDialog.askstring('Create ParseKnot', 'ParseKnot ID to create:')
        if not parseKnotId:return
        activeKnoth = self.xbmcThreads.threadDef
        knothType = self.xbmcThreads.getThreadAttr(activeKnoth, 'type')
        if self.xbmcThreads.createThread(iType = knothType, name = parseKnotId, menuId = parseKnotId) == -1: return
        if refKnot == None: refKnot = 'media' if knothType == 'thread' else 'rootmenu'
        lstChangedFlag = refKnot not in ['media', 'rootmenu']
        
        lstChanged = [] if lstChangedFlag else [self.xbmcThreads.getDotPath(parseKnotId)]
        self.xbmcThreads.threadDef = parseKnotId
        if knothType == 'list':
            if refKnot != 'rootmenu':
                if outputToRefKnoth:
                    lstChanged.append(self.xbmcThreads.getDotPath(activeKnoth))                    
                    if self.xbmcThreads.getThreadAttr(refKnot, 'up') != 'rootmenu':
                        refKnotUp = self.xbmcThreads.getThreadAttr(refKnot, 'up')
                        self.xbmcThreads.setNextThread(refKnotUp, parseKnotId)
                    self.xbmcThreads.setNextThread(parseKnotId, refKnot)
                    refKnot = parseKnotId
                else:
                    self.xbmcThreads.setNextThread(refKnot, parseKnotId)
                    activeKnoth = parseKnotId
        elif knothType == 'thread':
            self.setKnotParam('url', self.regexpEd.getActiveUrl())
            self.setRegexp()
            if refKnot != 'media':
                if outputToRefKnoth:
                    self.xbmcThreads.setNextThread(parseKnotId, refKnot)
                    activeKnoth = parseKnotId
                else:
                    lstChanged.append(self.xbmcThreads.getDotPath(activeKnoth))                    
                    if self.xbmcThreads.getThreadAttr(refKnot, 'up') != 'media':
                        refKnotUp = self.xbmcThreads.getThreadAttr(refKnot, 'up')
                        self.xbmcThreads.setNextThread(parseKnotId, refKnotUp)
                    self.xbmcThreads.setNextThread(refKnot, parseKnotId)
                    refKnot = parseKnotId
        if lstChangedFlag:
            lstChanged.append(self.xbmcThreads.getDotPath(activeKnoth))
        self.parseTree.refreshTreeInfo(parseKnotId, lstChanged = lstChanged)
        self.refreshRightPane()
        self.setSaveFlag(True)

    def setSaveFlag(self, state, lstChanged = None):
        suffix = '  **' if state else ''
        fileName = (self.currentFile if self.currentFile else 'default.pck')
        fileName = os.path.basename(fileName)
        self.title(fileName + suffix)
        if lstChanged:
            self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
            self.addonId.set(self.addonSettings.getParam('addon_id'))

    def importFile(self):
        name = tkFileDialog.askopenfilename(filetypes=[('xml Files', '*.xml'),('Text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            name = 'file:' + urllib.pathname2url(name)
            self.importUrl(name)
    
    def importUrl(self, urlToOpen = None, initialValue = None):
        if not urlToOpen:
            urlToOpen = tkSimpleDialog.askstring('Open URL', 'URL addres to parse:', initialvalue = initialValue or '')
        if urlToOpen:
            self.regexpEd.setActiveUrl(urlToOpen)

    def selectedURL(self):
        selRange = self.regexpEd.getSelRange()
        selUrl = self.regexpEd.getContent(*selRange)
        self.importUrl(selUrl)
        
    def selectedForm(self):
        selForm = self.regexpEd.getContent('1.0', 'end')
        if not (selForm[:5].lower() == '<form' and selForm[-8:-1].lower() == '</form>'):
            return tkMessageBox.showerror('Not Form', 'Zoom In to a <form.+?</form> pattern')
        selForm = '<form' + selForm[5:-8] + '</form>'
        activeUrl = self.regexpEd.getActiveUrl()
        formAttr = re.search('<form\s*([^>]+)>', selForm).group(1)
        formAttr = eval("dict(" + ",".join(formAttr.split()) + ")")
        method = '?' if formAttr.get("method",'GET') == 'GET' else '<post>'
        formUrl = formAttr.get('action', '') or activeUrl
        
        forInVars = re.findall(r'<input\s*(.+?)[/>]', selForm, re.IGNORECASE|re.DOTALL)
        urlVars = {}
        for inVar in forInVars:
            inVar = inVar.replace('class=', '_class=')
            inAttr = eval("dict(" + ",".join(inVar.split()) + ")")
            key = inAttr.get('name', None) or inAttr.get('id', None)
            if key:urlVars[key] = inAttr.get('value', '')
        methodData = urllib.urlencode(urlVars)
        selUrl = formUrl + method + methodData 
        self.importUrl(initialValue = selUrl)
         
    def newFile(self, fileName = '', threadData = None, modSourceCode = None , settings = None):
        self.checkSaveFlag()
        threadData = threadData or self.initThreadData()
        self.xbmcThreads.setThreadData(*threadData)

        addonSettings = settings or {}
        if addonSettings.has_key('reset'): addonSettings.pop('reset')
        self.addonSettings.setNonDefaultParams(addonSettings)

        self.vrtDisc._filegenerator.modSourceCode = modSourceCode or []
        self.parseTree.setXbmcThread(self.xbmcThreads)
        
        self.explorerTree.refreshFlag = True
        self.setActiveView(refreshFlag = True)

        self.activeKnot.set(self.xbmcThreads.threadDef)
        self.addonId.set(self.addonSettings.getParam('addon_id'))

        fileName = fileName or 'default.pck'
        D = os.path.dirname(fileName)
        if D: self.ideSettings.setParam('appdir_data', D)
        self.currentFile = fileName
        self.title(os.path.basename(self.currentFile))


    def saveFile(self):
        nameFile = self.currentFile
        self.saveAsFile(nameFile)
             
    def saveAsFile(self, nameFile = None):
        if not nameFile or nameFile == 'default.pck':
            nameFile = self.currentFile
            nameFile = nameFile.split('.')[0]
            appdir_data = os.path.abspath(self.ideSettings.getParam(srchSett = 'appdir_data'))
            nameFile = tkFileDialog.asksaveasfilename(initialdir=appdir_data, initialfile=nameFile, title = 'File Name to save', defaultextension='.pck',filetypes=[('pck Files', '*.pck'), ('All Files', '*.*')])
        if not nameFile: return
        try:
            with open(nameFile,'wb') as f:
                threads = self.xbmcThreads.getThreadData()
                settings = self.addonSettings.getNonDefaultParams()
                source = self.vrtDisc._filegenerator.modSourceCode
                objetos = [threads, settings, source]
                for objeto in objetos:
                    objStr = json.dumps(objeto)
                    f.write(objStr + '\n')
        except:
            tkMessageBox.showerror('Error', 'An error was found saving the file')
        else:
            self.currentFile = nameFile
            self.setSaveFlag(False)
            self.recFile(nameFile)

    def __openFile(self, filename=None):
        self.checkSaveFlag()
        if not filename:
            D = os.path.abspath(self.ideSettings.getParam(srchSett = 'appdir_data'))
            filename = tkFileDialog.askopenfilename(initialdir=D, filetypes=[('pck Files', '*.pck'), ('All Files', '*.*')])
        if filename:
            try:
                with open(filename,'rb') as f:
                    kodiThreadData = json.loads(f.readline())
                    settings = json.loads(f.readline())
                    modifiedCode = json.loads(f.readline())
            except IOError:
                tkMessageBox.showerror('Not a valid File', 'File not pck compliant ')
                return
            except ValueError:
                tkMessageBox.showerror('Not a valid File', 'An error has ocurred while reding the file ')
                return
            self.recFile(filename)
            self.newFile(fileName = filename, threadData = kodiThreadData, modSourceCode = modifiedCode, settings = settings )

    def recFile(self, filename):
        try:
            ndx = self.fileHistory.index(filename)
        except:
            pass
        else:
            self.fileHistory.pop(ndx)
        self.fileHistory.insert(0, filename)
        D = os.path.dirname(filename)
        self.ideSettings.setParam('appdir_data', D)
        nmax = self.ideSettings.getParam("file_opendoc").split('|', 1)[0]
        nmax = int(nmax)
        self.fileHistory = self.fileHistory[:nmax]
        self.ideSettings.setParam('var_fileHistory', json.dumps(self.fileHistory))
        self.ideSettings.save()

    def initThreadData(self):
        xbmcMenu = menuThreads.menuThreads()
        params = {'url':'https://www.youtube.com/watch?v=aCWRPqLt0wE', 'regexp':r'"adaptive_fmts":"(?P<youtube_fmts>[^"]+)"', 'compflags':'re.DOTALL'}
        xbmcMenu.setThreadParams('media', params)    

        xbmcMenu.lstChanged = []  # Se borra cualquier actualización del árbol 
                                  # porque este en este punto no existe
        return xbmcMenu.getThreadData()

class SplashScreen( object ):
   def __init__( self, tkRoot, imageFilename, minSplashTime=0 ):
      self._root              = tkRoot
      image = Image.open(imageFilename)
      self._image             = ImageTk.PhotoImage(image)
      self._splash            = None
      self._minSplashTime     = time.time() + minSplashTime

   def __enter__( self ):
      # Remove the app window from the display
      self.root_state = self._root.state()
      if self.root_state == 'normal':
          self._root.withdraw( )

      # Calculate the geometry to center the splash image
      scrnWt = self._root.winfo_screenwidth( )
      scrnHt = self._root.winfo_screenheight( )

      imgWt = self._image.width()
      imgHt = self._image.height()

      imgXPos = (scrnWt / 2) - (imgWt / 2)
      imgYPos = (scrnHt / 2) - (imgHt / 2)

      # Create the splash screen
      self._splash = tk.Toplevel()
      self._splash.overrideredirect(1)
      self._splash.geometry( '+%d+%d' % (imgXPos, imgYPos) )
      tk.Label( self._splash, image=self._image, cursor='watch' ).pack( )

      # Force Tk to draw the splash screen outside of mainloop()
      self._splash.update( )

   def __exit__( self, exc_type, exc_value, traceback ):
      # Make sure the minimum splash time has elapsed
      timeNow = time.time()
      if timeNow < self._minSplashTime:
         time.sleep( self._minSplashTime - timeNow )

      # Destroy the splash window
      self._splash.destroy( )

      # Display the application window
      if self.root_state == 'normal':
          self._root.deiconify( )

if __name__ == "__main__":
    Root = tk.Tk()
    Root.withdraw()
    ideSettings = xmlFileWrapper.xmlFileWrapper('IDE_Settings.xml', hasNonDefaultFile=True)
    importerPath = ideSettings.getParam('appdir_importer')
    importerPath = os.path.abspath(importerPath)
    bflag = not os.path.exists(os.path.join(importerPath, 'KodiScriptImporter.py'))
    if bflag:
        importerPath = tkFileDialog.askdirectory(title='Enter path for KodiScriptImporter module')
        ideSettings.setParam('appdir_importer', importerPath)
    sys.path.append(importerPath)
    try:
        import KodiScriptImporter
    except:
        tkMessageBox.showinfo('Kode IDE Info', 'KodiImporter not located')
    else:
        if bflag: ideSettings.save()
        with SplashScreen(Root, os.path.abspath(r'.\images\KodiIDE_logo.jpg'), 5.0 ):
            mainWin = XbmcAddonIDE()
        Root.wait_window(mainWin)

