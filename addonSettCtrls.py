'''
Created on 7/03/2015

@author: Alex Montes Barrios
'''
import Tkinter as tk
import xml.etree.ElementTree as ET
import tkMessageBox
from OptionsWnd import scrolledFrame

class vertRadioMenu(tk.Frame):
    def __init__(self, master = None, xmlFile = 'Addon_Settings.xml'):
        tk.Frame.__init__(self, master)
        self.refreshFlag = False
        self.intVar = tk.IntVar()
        self.setXmlFile(xmlFile)
        self.refreshPaneInfo()
        self.rightPane = None
        self.selOption(0)
        
    def setXmlFile(self, xmlFile):
        root = ET.parse(xmlFile).getroot()
        self.botonNames = root.findall('category')
        self.refreshFlag = True
        
    def setSettingsPane(self, settingPane):
        self.rightPane = settingPane
        
    def selOption(self, ene = None):
        if ene: self.intVar.set(ene) 
        selPane = self.intVar.get()
        if self.rightPane:
            self.rightPane.initFrameExec(selPaneIndx = selPane, saveChanges = True)

    def refreshPaneInfo(self):
        if not self.refreshFlag: return
        for child in self.children:child.forget()
        for k, elem in enumerate(self.botonNames):
            boton = tk.Radiobutton(self, width = 20, text = elem.get('label'), value = k, variable = self.intVar, command = lambda ene = k: self.selOption(ene), indicatoron = 0, name = 'but' + str(k))
            boton.pack(side = tk.TOP, fill = tk.X)
        self.refreshFlag = False
        
class settingsDisplay(tk.Frame):
    def __init__(self, master = None, xmlFile = 'Addon_Settings.xml', nonDefaultValues = None):
        tk.Frame.__init__(self, master)
        self.root = ET.parse(xmlFile).getroot()
        self.setNonDefaultParams(nonDefaultValues)
        self.topPane = None
        self.scrolled = None
        self.setGUI()
        
    def setNonDefaultParams(self, nonDefSettings):
        self.settings = nonDefSettings or {}
        
    def getNonDefaultParams(self):
        return self.settings
        
    def setGUI(self):
        topPane = tk.Frame(self, height = 500, width = 500)
        topPane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        topPane.grid_propagate(0)
        self.topPane = topPane
        bottomPane = tk.Frame(self, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.BOTTOM, fill = tk.X)
        for label in ['Apply', 'Discard']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, command = lambda action = label: self.onAction(action))
            boton.pack(side = tk.RIGHT)
        self.bottomPane = bottomPane
        
    def onAction(self, action, inChangedSettings = None):
        changedSettings = inChangedSettings or self.scrolled.getChangeSettings(self.settings)
        if action == 'Apply':
            reset = changedSettings.pop('reset')
            for key in reset: self.settings.pop(key)
            self.settings.update(changedSettings)
        if action == 'Discard':
            widgets = self.changedWidgets(changedSettings)
            map(lambda w: w.setValue(self.settings.get(w.id, w.default)), widgets)

    def initFrameExec(self, *args, **kwargs):
        self.changesettings(0)

    def changesettings(self, selPaneIndx):
        if self.scrolled:
            noDefault = self.scrolled.getChangeSettings(self.settings)
            widgets = self.changedWidgets(noDefault)
            if widgets:
                map(lambda w: w.config(bg='yellow'), widgets)
                message = 'Some <category> settings has been change, do you want to apply them?'
                message = message.replace('<category>', self.scrolled.category) 
                if tkMessageBox.askokcancel('Change Settings', message):
                    self.onAction('Apply', noDefault)
            self.scrolled.forget()
        selPane = self.root.findall('category')[selPaneIndx]        
        self.scrolled = scrolledFrame(self.topPane, self.settings, selPane)

    def changedWidgets(self, changedSettings):
        reset = list(changedSettings['reset'])
        reset += changedSettings.keys()
        reset.remove('reset')
        widgets = []
        if reset:
            filterFlag = lambda widget: (hasattr(widget, 'id') and (widget.id in reset)) 
            widgets = self.scrolled.widgets(filterFlag)
        return widgets
    
    def getParam(self, srchSett = None):
        root = self.root
        if not srchSett:
            settings = {}
            for elem in root.findall('.//setting[@default]'):
                settings[elem.get('id')] = elem.get('default')
            settings.update(self.settings)
        else:
            if self.settings.has_key(srchSett): return self.settings[srchSett]
            srchStr = './/setting[@id="' + srchSett + '"]'
            settings = root.findall(srchStr)
            settings = settings[0].get('default') if settings else ''
        return settings
