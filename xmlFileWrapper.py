'''
Created on 19/03/2015

@author: Alex Montes Barrios
'''
import Tkinter as tk
import xml.etree.ElementTree as ET
import tkMessageBox
import json
import os
from PIL import Image, ImageTk
import menuThreads
import ParseThreads
import CustomRegEx
from OptionsWnd import scrolledFrame


class xmlFileWrapper():
    def __init__(self, xmlFile, **kwargs):
        if kwargs.get('isFile', True):
            self.root = ET.parse(xmlFile).getroot()
        else:
            self.root = ET.fromstring(xmlFile)
        self.paneId = 'category'
        self.ver = 0
        self.refreshFlag = False
        nonDefaultValues = None
        if kwargs.has_key('nonDefaultValues'):
            nonDefaultValues = kwargs['nonDefaultValues']
        elif kwargs.has_key('hasNonDefaultFile'):
            if kwargs['hasNonDefaultFile']:
                prefix, suffix = os.path.splitext(xmlFile)
                self.nonDefaultFile = nonDefaultFile = prefix + '_nDP' + suffix
                if os.path.exists(nonDefaultFile):
                    with open(nonDefaultFile, 'rb') as fp:
                        content = fp.read()
                    pattern = r'(?#<setting id=id value=value>)'
                    nonDefaultValues = dict(CustomRegEx.findall(pattern, content))
        self.setNonDefaultParams(nonDefaultValues)
        self.setActivePaneIndx()

    def save(self):
        if hasattr(self, 'nonDefaultFile'):
            content = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>'
            content += '\n<settings>\n    '
            content += '\n    '.join(map(lambda x: '<setting id="%s" value="%s" />' % x, self.settings.items()))
            content += '\n</settings>'
            with open(self.nonDefaultFile, 'wb') as fp:
                fp.write(content)

    def getVer(self):
        return self.ver
    
    def setPaneId(self, paneId):
        self.paneId = paneId
        
    def setNonDefaultParams(self, nonDefSettings, refreshFlag = True):
        self.settings = nonDefSettings or {}
        self.refreshFlag = refreshFlag
        self.ver += 1
        
    def getNonDefaultParams(self):
        return self.settings

    def processChangedSettings(self, changedSettings):
        if changedSettings.has_key('reset'):
            toReset = changedSettings.pop('reset')
            for key in toReset:
                self.settings.pop(key)
        self.settings.update(changedSettings)

    def getParam(self, srchSett = None):
        root = self.root
        if not srchSett:
            settings = {}
            for elem in root.findall('.//setting[@default]'):
                settings[elem.get('id')] = elem.get('default')
            settings.update(self.settings)
        else:
            if self.settings.has_key(srchSett): return self.settings[srchSett]
            settings = self.getDefault(srchSett)
        return settings

    def getDefault(self, srchSett):
        srchStr = './/setting[@id="' + srchSett + '"]'
        settings = self.root.findall(srchStr)
        settings = settings[0].get('default') if settings else ''
        return settings

    def resetParam(self, srchSett):
        if not self.isDefault(srchSett):
            self.settings.pop(srchSett)

    def setParam(self, settKey, value):
        if self.getDefault(settKey) != value:
            self.settings[settKey] = value
        else:
            self.resetParam(settKey)

    def keys(self):
        params = self.getParam()
        return params.keys()

    def getActivePaneLabel(self):
        activePane = self.getActivePane()
        return activePane.attrib['label']

    def isActivePaneLocked(self):
        return False

    def isDefault(self, settKey):
        return not self.settings.has_key(settKey)
    
    def getActivePane(self):
        return self.root.findall(self.paneId)[self.actPaneIndx]        

    def setActivePaneIndx(self, index = 0):
        self.actPaneIndx = index
        
class threadXmlFileWrapper(xmlFileWrapper):
    def __init__(self, xmlFile, kodiThreads):
        xmlFileWrapper.__init__(self, xmlFile)
        self.kodiThreads = kodiThreads

    def getActivePaneLabel(self):
        kodiThreads = self.kodiThreads
        return kodiThreads.threadDef

    def isActivePaneLocked(self):
        threadId = self.getActivePaneLabel()
        return self.kodiThreads.isthreadLocked(threadId)

    def getActivePane(self):
        threadId = self.kodiThreads.threadDef
        threadType = self.kodiThreads.getThreadAttr(threadId, 'type')
        srchStr = './/category[@label="' + threadType + '"]'
        threadPane = self.root.find(srchStr)
        settings = self.getNodeSettings(threadId, threadType, threadPane)
        self.setNonDefaultParams(settings, refreshFlag = False) 
        return threadPane
    
    def getNodeSettings(self, nodeId, nodeType, nodeConfigData):
        nodeDataIds = [key.get('id') for key in nodeConfigData.findall('setting') if key.get('id', None)]
        settings = dict(self.kodiThreads.parseThreads[nodeId])
        params = settings.pop('params')
        settings['nodeId'] = nodeId
        if settings.has_key('up'):
            baseNode = 'rootmenu' if nodeType == 'list' else 'media'
            lista = [elem for elem in self.kodiThreads.getSameTypeNodes(baseNode) if not elem.endswith('_lnk')]
            upMenu = '|'.join([settings['up']] + sorted(lista)) if nodeId != 'media' else ''
            settings['upmenu'] = upMenu
        other = set(params.keys()).difference(nodeDataIds)
        if len(other):
            params = dict(params)
            otherParameters = '|'.join([key + ',' + str(params.pop(key)) for key in other])
            settings['otherparameters'] = otherParameters
        settings.update(params)
        return settings
    
    def processChangedSettings(self, changedSettings):
        nodeId = self.settings['nodeId']
        nodeParams = self.kodiThreads.getThreadAttr(nodeId,'params')
        parameters = {}
        if changedSettings.has_key('otherparameters') or 'otherparameters' in changedSettings['reset']:
            if self.settings.has_key('otherparameters'):
                oldOther = [tuple(elem.split(',')) for elem in self.settings['otherparameters'].split('|')]
                for elem in oldOther:
                    key = elem[0]
                    nodeParams.pop(key)
        for key in changedSettings.pop('reset'):
            self.settings.pop(key)
            if nodeParams.has_key(key): nodeParams.pop(key)
        if changedSettings.get('otherparameters', None):
            otherParameters = [tuple(elem.split(',')) for elem in changedSettings['otherparameters'].split('|')]
            parameters.update(otherParameters)
        for elem in  set(changedSettings.keys()).difference(['otherparameters', 'nodeId', 'upmenu', 'name']):
            parameters[elem] = changedSettings[elem]
        if parameters: nodeParams.update(parameters)

        nodeFlag = nodeId in ['media', 'rootmenu']
        if nodeFlag:
            for key in ['nodeId', 'upmenu']:
                if changedSettings.has_key(key): changedSettings.pop(key)

        lstChanged = []
        if changedSettings.has_key('nodeId'):
            lstChanged.append(self.kodiThreads.getDotPath(self.settings['nodeId']))
            self.kodiThreads.rename(self.settings['nodeId'], changedSettings['nodeId'])
            lstChanged.append(self.kodiThreads.getDotPath(changedSettings['nodeId']))
            nodeId = changedSettings['nodeId']
        if changedSettings.has_key('name'):
            self.kodiThreads.parseThreads[nodeId]['name'] = changedSettings['name']
        if changedSettings.has_key('upmenu'):
            upmenu = changedSettings['upmenu'].partition('|')[0]
            if  upmenu != self.settings['up']:
                changedSettings['up'] = upmenu
                kType = self.kodiThreads.getThreadAttr(nodeId, 'type')
                threadIn = (upmenu, nodeId) if kType == 'list' else (nodeId, upmenu)
                lstChanged.append(self.kodiThreads.getDotPath(nodeId))
                self.kodiThreads.setNextThread(*threadIn)
                lstChanged.append(self.kodiThreads.getDotPath(nodeId))
        self.settings.update(changedSettings)
#         if self.notifyChangeTo: self.notifyChangeTo(True, lstChanged)



class settingsDisplay(tk.Frame):
    def __init__(self, master = None, xmlFileW = None):
        tk.Frame.__init__(self, master)
        self.setXmlFileW(xmlFileW)
        self.notifyChange = None
        self.middlePane = None
        self.scrolled = None
        self.selPaneLabel = ''
        self.setGUI()
        
    def setXmlFileW(self, xmlFileW):
        self.xmlFileW = xmlFileW
        
    def setNotifyChange(self, notifyProcess):
        self.notifyChange = notifyProcess
        
    def setGUI(self):
        topPane = tk.Frame(self, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        topPane.pack(side = tk.TOP, fill = tk.X)
        self.topPane = topPane
        imPath = os.path.abspath('./images/lockIcon.png')
        lockImg = Image.open(imPath)
        lockImg.thumbnail((20,20), Image.ANTIALIAS)
        self.lockImg = ImageTk.PhotoImage(lockImg)
        label = tk.Label(topPane, name='menuid', text="menuID",
                         compound=tk.LEFT,
                         font=('Times', '24', 'bold italic'))
        label.pack(fill=tk.X, expand=tk.YES)
        middlePane = tk.Frame(self, height = 500, width = 500)
        middlePane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        middlePane.grid_propagate(0)
        self.middlePane = middlePane
        bottomPane = tk.Frame(self, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.BOTTOM, fill = tk.X)
        for label in ['Apply', 'Discard']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, command = lambda action = label: self.onAction(action))
            boton.pack(side = tk.RIGHT)
        self.bottomPane = bottomPane
        
    def onAction(self, action, inChangedSettings = None):
        settings = self.xmlFileW.getNonDefaultParams()
        changedSettings = inChangedSettings or self.scrolled.getChangeSettings(settings)
        if action == 'Apply':
            self.xmlFileW.processChangedSettings(changedSettings)
            if self.notifyChange: self.notifyChange(True)
        if action == 'Discard':
            widgets = self.changedWidgets(changedSettings)
            map(lambda w: w.setValue(settings.get(w.id, w.default)), widgets)

    def initFrameExec(self, refreshFlag=False, selPaneIndx = None, saveChanges =False):
        self.changesettings(selPaneIndx, saveChanges)
        children = self.bottomPane.children
        defNode = self.xmlFileW.getActivePaneLabel()
        self.topPane.children['menuid'].config(text=defNode)
        bFlag = self.xmlFileW.isActivePaneLocked()
        image = self.lockImg if bFlag else ''
        btnstate = tk.DISABLED if bFlag else tk.NORMAL
        self.topPane.children['menuid'].config(image=image)
        children['apply'].config(state=btnstate)
        children['discard'].config(state=btnstate)

    def changesettings(self, selPaneIndx = None, saveChanges = True):
        if selPaneIndx is None:
            selPaneIndx = self.xmlFileW.actPaneIndx
        else:
            self.xmlFileW.setActivePaneIndx(selPaneIndx)
        if saveChanges and self.scrolled and not self.xmlFileW.refreshFlag:
            settings = self.xmlFileW.getNonDefaultParams()
            noDefault = self.scrolled.getChangeSettings(settings)
            widgets = self.changedWidgets(dict(noDefault))
            if widgets:
                oldBg = widgets[0].cget('bg')
                map(lambda w: w.config(bg='yellow'), widgets)
                message = 'Some <category> settings has been change, do you want to apply them?'
                message = message.replace('<category>', self.scrolled.category) 
                if tkMessageBox.askokcancel('Change Settings', message):
                    self.onAction('Apply', noDefault)
                map(lambda w: w.config(bg=oldBg), widgets)
        self.xmlFileW.refreshFlag = False
        selPane = self.xmlFileW.getActivePane()
        settings = self.xmlFileW.getNonDefaultParams()        
        if self.selPaneLabel != selPane.get('label'):
            if self.scrolled: self.scrolled.forget()
            self.scrolled = scrolledFrame(self.middlePane, settings, selPane)
            self.selPaneLabel = selPane.get('label')
        else:
            self.scrolled.modifySettingsValues(settings)

    def changedWidgets(self, changedSettings):
        reset = changedSettings.pop('reset') + changedSettings.keys()
        filterFlag = lambda widget: (hasattr(widget, 'id') and (widget.id in reset))
        return self.scrolled.widgets(filterFlag)
    
