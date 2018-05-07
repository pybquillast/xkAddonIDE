'''
Created on 18/09/2014

@author: Alex Montes Barrios
'''

import Tkinter as tk
import tkSimpleDialog
import tkFileDialog
import menuThreads
import ttk
import tkFont
import urllib2
import tkMessageBox
import urlparse
from functools import partial
import xml.etree.ElementTree as ET
import os
import fnmatch
import re
import shutil
import zipfile
import operator
import importlib

import StringIO
# import xmlFileWrapper

def widgetFactory(master, settings, selPane, panelModule=None, k=-1):
    widgetTypes = dict(sep=settSep, lsep=settSep,
                       text=settText,
                       optionlst=settOptionList,
                       number=settNumber, ipaddress=settNumber,
                       slider=settSlider,
                       bool=settBool,
                       enum=settEnum, labelenum=settEnum,
                       drpdwnlst=settDDList,
                       file=settFile, audio=settFile, video=settFile, image=settFile, executable=settFile,
                       folder=settFolder,
                       fileenum=settFileenum,
                       action=settAction,
                       container=settContainer,
                       scrolledcontainer=settScrolledContainer)

    if not panelModule and selPane.get('lib'):
        panelModule = selPane.get('lib')
        panelModule = importlib.import_module(panelModule)
    enableEc = []
    for setting in selPane.findall('setting'):
        k += 1
        options = setting.attrib
        options['name'] = str(k)
        if options.get('enable', None):
            enableEc.append((k, setting.attrib['enable']))
        wType = options.get('type')
        widgetClass = widgetTypes.get(wType, None)
        assert widgetClass is not None, 'The setting type "%s" is not a define type. \n' \
                                        'It must me one of: %s ' % (wType, ', '.join(sorted(widgetTypes.keys())))
        wId = options.get('id')
        if wId and panelModule and hasattr(panelModule, wId):
            idClass = getattr(panelModule, wId)
            assert issubclass(idClass, widgetClass), \
                'In module %s the class "%s" must be ' \
                'inherited from %s' % (panelModule.__name__, wId, widgetClass.__name__)
            setattr(idClass, 'me', master)
            widgetClass = idClass

        dummy = widgetClass(master, **options)
        if wType in ['container', 'scrolledcontainer']:
            wcontainer = dummy
            if wType == 'scrolledcontainer': wcontainer = wcontainer.innerframe
            k, deltEnableEc = widgetFactory(wcontainer, settings, setting, panelModule=panelModule, k=k)
            enableEc += deltEnableEc
        if hasattr(dummy, 'id'):
            key = dummy.id
            if settings and settings.has_key(key):
                dummy.setValue(settings[key])
            dummy.form.registerWidget(key, dummy.path)
    return k, enableEc

class formFrame(tk.Frame):
    def __init__(self, master, settings, selPane, background="SystemButtonFace"):
        tk.Frame.__init__(self, master, background=background)
        self.settings = {}
        self.enEquations = {}
        self.dependents = {}
        self.widgetMapping = {}
        self.nameToId = {}
        self.radioGroups = {}
        self.frame = frame = settContainer(self, name="frame")
        frame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)

        self.populateWithSettings(settings, selPane)

    def __getattr__(self, attr):
        if attr in self.__dict__['widgetMapping']:
            widgetMapping = self.__dict__['widgetMapping']
            wpath = widgetMapping.get(attr)
            widget = self
            while wpath:
                wdName, wpath = wpath.partition('.')[0:3:2]
                widget = widget.nametowidget(wdName)
            return widget
        raise AttributeError()

    def populateWithSettings(self, settings, selPane):
        enableEq = widgetFactory(self.frame, settings, selPane)[1]
        self.nameToId = {value.rsplit('.', 1)[-1]:key for key, value in self.widgetMapping.items()}
        self.category = selPane.get('label')
        self.registerEc(enableEq)
        self.setDependantWdgState()
        self.registerChangeListeners()

    def setChangeSettings(self, settings):
        form = self
        mapping = [key for key in self.widgetMapping.keys()
                   if hasattr(getattr(form, key), 'setValue')]
        toModify = set(settings.keys()).intersection(mapping)
        map(lambda w: w.setValue(settings[w.id]), self.getWidgets(toModify))
        toReset = set(mapping).difference(toModify)
        map(lambda w: w.setValue(w.default), self.getWidgets(toReset))

    def registerEc(self, enableEquations):
        for posWidget, enableEc in enableEquations:
            enableEc = self.getAbsEcuation(posWidget, enableEc)
            wVars = map(str, self.findVars(enableEc))
            assert set(wVars).issubset(self.nameToId), 'The enable equation for "%s" widget' \
                                                       ' reference a non id widget' \
                                                       % (self.nameToId[str(posWidget)])
            for elem in wVars:
                self.dependents[elem] = self.dependents.get(elem,[]) + [str(posWidget)]
            self.enEquations[str(posWidget)] = enableEc.replace('+', ' and ')

    def getAbsEcuation(self, pos, enableEc):
        for tag in ['eq(', 'lt(', 'gt(']:
            enableEc = enableEc.replace(tag, tag + '+')
        enableEc = enableEc.replace('+-', '-').replace('!', 'not ')
        enableEc = enableEc.replace('true','True').replace('false','False').replace(',)',',None)')
        for tag in ['eq(', 'lt(', 'gt(']:
            enableEc = enableEc.replace(tag, tag + str(pos))
        return enableEc

    def findVars(self, enableEc):
        enableEc = enableEc.replace('not ', '').replace('*', '+')
        eq = lt = gt = lambda x, a: [x]
        vars = eval(enableEc)
        try:
            retval = set(vars)
        except:
            retval = []
        else:
            retval = list(retval)
        return retval
        # return [elem for k, elem in enumerate(vars) if elem not in vars[0:k]]

    def findWidgetState(self, enableEq):
        eq = lambda x,a:getattr(self, self.nameToId[str(x)]).getValue() == a
        lt = lambda x,a:getattr(self, self.nameToId[str(x)]).getValue() < a
        gt = lambda x,a:getattr(self, self.nameToId[str(x)]).getValue() > a
        state = eval(enableEq) >= 1
        return tk.NORMAL if state else tk.DISABLED

    def setDependantWdgState(self):
        for key in sorted(self.enEquations.keys(), key = int):
            enableEq = self.enEquations[key]
            calcState = self.findWidgetState(enableEq)
            widget = getattr(self, self.nameToId[key])
            try:
                idKey = widget.id
                widget.children[idKey].configure(state = calcState)
            except:
                pass

    def registerChangeListeners(self):
        for key in self.dependents.keys():
            widget = getattr(self, self.nameToId[key])
            widget.setListener(self.varChange)

    def varChange(self, widgetName):
        for depname in self.dependents[widgetName]:
            enableEq = self.enEquations[depname]
            calcState = self.findWidgetState(enableEq)
            widget = getattr(self, self.nameToId[depname])
            try:
                idKey = widget.id
                widget.children[idKey].configure(state=calcState)
            except:
                pass

    def registerWidget(self, wdId, wdPath):
        self.widgetMapping[wdId] = wdPath

    def getWidgets(self, widgetsIds=None):
        widgetsIds = widgetsIds or self.widgetMapping.keys()
        return [getattr(self, key) for key in widgetsIds]

    def getGroupVar(self, groupName):
        return self.radioGroups.setdefault(groupName, tk.StringVar())

    def getGroupValue(self, groupName):
        return self.radioGroups[groupName].get()

    def getChangeSettings(self, settings):
        changedSettings = dict(reset = [])
        for child in self.getWidgets():
            try:
                flag = child.isValueSetToDefault()
            except:
                pass
            else:
                key, value = child.getSettingPair()
                if not flag:
                    changedSettings[key] = value
                elif key and settings.has_key(key):
                    changedSettings['reset'].append(key)
        filterFlag = lambda key: (not settings.has_key(key) or settings[key] != changedSettings[key])
        toProcess = dict([(key, value) for key, value in changedSettings.items() if filterFlag(key)])
        return toProcess

class scrolledFrame(tk.Frame):
    def __init__(self, master, settings, selPane):
        self.initDescenAscend()
        tk.Frame.__init__(self, master)
        self.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        self.canvas = tk.Canvas(self, borderwidth=0, background="SystemButtonFace")
        self.category = selPane.get('label')
        self.frame = formFrame(self.canvas, settings, selPane, background="SystemButtonFace")
        self.frame.pack()

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")
        self.canvas.bind("<Configure>", self.OnCanvasConfigure)

    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        print 'onFrame'
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def OnCanvasConfigure(self, event):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        self.frame.configure(width = event.width, height = y2-y1)
        self.frame.pack_propagate(0)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def modifySettingsValues(self, settings, filterFlag = lambda widget: hasattr(widget, 'id')):
        widgets = self.widgets(filterFlag)
        map(lambda w: w.setValue(settings.get(w.id, w.default)), widgets)

    def initDescenAscend(self):
        self.settings = {}
        self.enEquations = {}
        self.dependents = {}
        self.widgetMapping = {}

    def getChangeSettings(self, settings):
        interiorFrame = self.frame
        changedSettings = dict(reset = [])
        for child in interiorFrame.getWidgets():
            try:
                flag = child.isValueSetToDefault()
            except:
                pass
            else:
                key, value = child.getSettingPair()
                if not flag:
                    changedSettings[key] = value
                elif key and settings.has_key(key):
                    changedSettings['reset'].append(key)
        filterFlag = lambda key: (not settings.has_key(key) or settings[key] != changedSettings[key])
        toProcess = dict([(key, value) for key, value in changedSettings.items() if filterFlag(key)])
        return toProcess

    def widgets(self, filterFunc = None):
        allWidgets = self.frame.getWidgets()
        return [aWidget for aWidget in allWidgets if filterFunc(aWidget)] if filterFunc else allWidgets

    def getAllSettings(self, keyfunc = None):
        keyfunc = keyfunc or operator.attrgetter('id')
        allwidgets = self.frame.getWidgets()
        allwidgets.sort(key = keyfunc)
        return [widget.getSettingPair(tId = True) for widget in allwidgets]

class baseWidget(tk.Frame):
    def __init__(self, master, **options):
        self._id = options.pop('id')
        wdgName = options.get('name').lower()
        if options.has_key('varType'): self.setVarType(options.pop('varType'))
        self.default = None
        baseConf = dict(name=wdgName, bd=1, highlightbackground='dark grey', highlightthickness=2,
                        highlightcolor='green', takefocus=1)
        baseConf.update(options)
        if isinstance(master, settContainer) or isinstance(master, settScrolledContainer):
            self.path = master.path + '.' + baseConf.get('name', '')
            self.form = master.form
        else:
            self.path = baseConf.get('name', '')
            self.form = master
        tk.Frame.__init__(self, master, **baseConf)
        packSide = master.side if isinstance(master, settContainer) else tk.TOP
        self.pack(side=packSide, fill=tk.X, ipadx=2, ipady=2, padx=1, pady=1)

    def setVarType(self, varType='string'):
        if varType == 'int':
            self.value = tk.IntVar()
        elif varType == 'double':
            self.value = tk.DoubleVar()
        elif varType == 'boolean':
            self.value = tk.BooleanVar()
        else:
            self.value = tk.StringVar()

    def getSettingPair(self, tId=False):
        id = self._id if tId else self.id
        return (id, self.getValue())

    def isValueSetToDefault(self):
        return self.getValue() == self.default

    def setValue(self, value):
        self.value.set(value)

    def getValue(self):
        return self.value.get()

    def setListener(self, function):
        self.listener = function
        self.value.trace("w", self.callListener)

    def callListener(self, *args):
        self.listener(self.name)

class settLabel(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT, fill = tk.X, expand = 1)

class myScrolledList(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.setGUI()
        self.bind_all('<Down>', self.nextWidget)
        self.bind_all('<Up>', self.prevWidget)
        self.widgetContainer.children['label0'].focus_force()

    def nextWidget(self, event):
        name = event.widget.name
        k = (int(name[5:]) + 1) % 15
        widget = self.widgetContainer.children['label' + str(k)]
        place_info = self.widgetContainer.place_info()
        if widget.winfo_y() + int(place_info['y']) < 0:
            place_info['y'] = 0
            self.widgetContainer.place(**place_info)
            page = self.leftPane.winfo_height()
            last = float((1.0*page)/self.widgetContainer.winfo_height())
            self.vsb.set(0, last)
        elif widget.winfo_y() + widget.winfo_height() + int(place_info['y']) > self.leftPane.winfo_height():
            self.yview(tk.SCROLL, 1, tk.UNITS)
        widget.focus_force()
        return 'break'

    def prevWidget(self, event):
        name = event.widget.name
        k = (int(name[5:]) + 15 - 1) % 15
        widget = self.widgetContainer.children['label' + str(k)]
        place_info = self.widgetContainer.place_info()
        if widget.winfo_y() + int(place_info['y']) > self.leftPane.winfo_height():
            page = self.leftPane.winfo_height()
            place_info['y'] = page - self.widgetContainer.winfo_height()
            self.widgetContainer.place(**place_info)
            first = float(abs(1.0*place_info['y'])/self.widgetContainer.winfo_height())
            self.vsb.set(first, 1.0)
        elif widget.winfo_y() + int(place_info['y']) < 0:
            self.yview(tk.SCROLL, -1, tk.UNITS)
        widget.focus_force()
        return 'break'


    def setGUI(self):
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.yview)
        self.vsb.pack(side = tk.RIGHT, fill = tk.Y)

        self.leftPane = tk.Frame(self, width = 100, height = 180)
        self.leftPane.pack(side = tk.LEFT, fill = tk.BOTH, expand = tk.YES)
        self.leftPane.pack_propagate(0)
        self.widgetContainer = tk.Frame(self.leftPane)
        for k in range(15):
            label = settLabel(self.widgetContainer, name = 'label' + str(k), label = 'Opcion ' + str(k))
        self.widgetContainer.place(relwidth = 1.0, y = 0)

    def yview(self, mType, nUnits, uType = None):
        page = self.leftPane.winfo_height()
        step = self.widgetContainer.winfo_height()/len(self.widgetContainer.children)
        posMax = page - self.widgetContainer.winfo_height()
        place_info = self.widgetContainer.place_info()
        if mType == tk.SCROLL:
            if uType == tk.UNITS:
                deltaPos = -int(nUnits) * step
            elif uType == tk.PAGES:
                deltaPos = -int(nUnits) * page
            place_info['y'] = min(0, max(posMax, int(place_info['y']) + deltaPos))
        elif mType == tk.MOVETO:
            deltaPos = int(float(nUnits) * self.widgetContainer.winfo_height())/step
            place_info['y'] = -deltaPos * step
        self.widgetContainer.place(**place_info)
        first = float(abs(1.0*place_info['y'])/self.widgetContainer.winfo_height())
        last = first + float((1.0*page)/self.widgetContainer.winfo_height())
        self.vsb.set(first, last)


class settFileenum(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        spBoxValues = self.getFileList(options)
        tk.Spinbox(self, name = self.id, textvariable = self.value, values = spBoxValues).pack(side = tk.RIGHT, fill = tk.X, expand = 1)

    def getFileList(self, options):
        basepath = os.path.abspath('.')
        values = options.get('values','')
        mypath = os.path.join(basepath, values)
        if not os.path.exists(mypath): return
        dirpath, dirnames, filenames = os.walk(mypath).next()
        if options.get('mask', None) == '/':
            return dirnames
        else:
            mask = options.get('mask', None)
            filenames = [elem for elem in filenames if fnmatch.fnmatch(elem, mask)]
            if options.get('hideext', 'true') == 'true':
                filenames  = [elem.split('.')[0] for elem in filenames]
            return filenames

class settFolder(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        tk.Button(self, name = self.id, textvariable = self.value, command = self.getFolder ).pack(side = tk.RIGHT, fill = tk.X, expand = 1)

    def getFolder(self):
        folder = tkFileDialog.askdirectory()
        if folder:
            self.value.set(folder)

class settFile(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        tk.Button(self, name = self.id, anchor = 'e', textvariable = self.value, command = self.getFile ).pack(side = tk.RIGHT, fill = tk.X, expand = 1)

    def getFile(self):
        fileName = tkFileDialog.askopenfilename()
        if fileName:
            self.value.set(fileName)

class settDDList(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.spBoxValues = options.get('values').split('|')
        self.lvalues = spBoxValues = options.get('lvalues').split('|')
        tk.Spinbox(self, name = self.id, command=self.onChangeSel, textvariable = self.value, values = spBoxValues).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        self.setValue(self.default)

    def setValue(self, value):
        try:
            ndx = self.spBoxValues.index(value)
        except:
            return
        self.value.set(self.lvalues[ndx])

    def getValue(self):
        try:
            ndx = self.lvalues.index(self.value.get())
        except:
            return
        return self.spBoxValues[ndx]

    def onChangeSel(self):
        pass

class settEnum(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        if options.has_key('values'):
            spBoxValues = options.get('values').split('|')
        else:
            spBoxValues = options.get('lvalues').split('|')
        tk.Spinbox(self, name = self.id, textvariable = self.value, values = spBoxValues).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        self.setValue(self.default)


    def setValue(self, value):
        nPos = value.find('|')
        self.withValues = withValues = nPos != -1
        if withValues:
            spBoxValue = value[nPos + 1:].split('|')
            self.children[self.id].configure(values = spBoxValue)
            value = value[:nPos]
        self.value.set(value)

    def getValue(self, onlyValue = False):
        onlyValue = onlyValue or not self.withValues
        if onlyValue: return self.value.get()
        return  '|'.join([self.value.get()] + self.children[self.id].cget('values').split(' '))

    def getSettingPair(self, tId = False):
        id = self._id if tId else self.id
        return (id, self.getValue(tId))


class settOptionList(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        self.isTree = options.get('tree', 'false') == 'true'
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        settSep(self, name = 'label', type = 'lsep', label = options.get('label')).pack(side = tk.TOP, fill = tk.X)

        if options.get('id'): self.id = options.get('id').lower().replace('.', '__')
        self.default = options.get('default', '')

        uFrame = tk.Frame(self)
        uFrame.pack(side = tk.TOP, fill = tk.BOTH)

        sbar = tk.Scrollbar(uFrame)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        colHeadings = options.get('columnsheadings')
        dshow = 'headings'
        columnsId = dcolumns = map(lambda x: x.strip(),colHeadings.split(','))
        if self.isTree:
            dshow = 'tree ' + dshow
            dcolumns = '#all'
        tree = ttk.Treeview(uFrame, show=dshow, columns = columnsId, displaycolumns = dcolumns)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand = 1)
        sbar.config(command=tree.yview)                    # xlink sbar and tree
        tree.config(yscrollcommand=sbar.set)               # move one moves other
        for column in columnsId:
            tree.heading(column, text = column, anchor = tk.W)
        self.tree = tree
        self.columnsId = columnsId

        bFrame = tk.Frame(self)
        bFrame.pack(side = tk.BOTTOM, fill = tk.X)
        boton = tk.Button(bFrame, text = 'Add', width = 15, command = self.onAdd)
        boton.pack(side = tk.LEFT)
        boton = tk.Button(bFrame, text = 'Edit', width = 15, command = self.onEdit)
        boton.pack(side = tk.LEFT)
        boton = tk.Button(bFrame, text = 'Del', width = 15, command = self.onDel)
        boton.pack(side = tk.RIGHT)

        self.setValue(self.default)

    def xmlDlgWindow(self, tupleSett, isEdit=False, isTree=False):
        header = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<settings>
    <category label="TCombobox">
"""
        footer = """    </category>
</settings>
"""
        outStr = header
        if not isEdit and isTree:
            deltaStr = '<setting id="{0}" type="text" label="Parent Element" default="{1}" enable="false"/>\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[0])
            deltaStr = '<setting id="{0}" type="text" label="Element Name" default="{1}" />\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[1])
            tupleSett = tupleSett[2:]

        templateStr = '<setting id="{0}" type="text" label="{0}" default=""/>\n'
        if isEdit:
            templateStr = '<setting id="{0}" type="text" label="{0}" default="{1}"/>\n'
        for x, y in tupleSett:
            deltaStr = templateStr.format(x, y)
            outStr += 8*' ' + deltaStr
        outStr += footer
        return outStr

    def onAdd(self):
        parent = self.tree.focus()
        pair = [(col, col) for col in self.columnsId]
        if self.isTree:
            pair = [('parent', self.tree.item(parent, 'text')), ('text', '')] + pair
        xmlDlg = self.xmlDlgWindow(pair,isEdit=False, isTree=self.isTree)
        dlg = TreeDialog(self, title='Add', xmlFile=xmlDlg, isFile=False)
        if dlg.allSettings:
            result = dict(dlg.allSettings)
            columnsId = self.columnsId
            if self.isTree:
                columnsId = ['text'] + columnsId
            record = [result[col].strip() for col in columnsId]
            parent, iid, text = parent, None, ''
            if self.isTree:
                text = record[0]
                record = record[1:]
            self.tree.insert(parent, 'end', iid=iid, text=text, values=record, open=True)

    def onEdit(self):
        iid = self.tree.focus()
        if iid:
            value = self.tree.set
            columnsId = self.columnsId
            pair = [(col, value(iid, col)) for col in columnsId]
            xmlDlg = self.xmlDlgWindow(pair, isEdit=True)
            dlg = TreeDialog(self, title='Edit', xmlFile=xmlDlg, isFile=False)
            if dlg.allSettings:
                result = dict(dlg.allSettings)
                record = [result[col].strip() for col in columnsId]
                for k, col in enumerate(columnsId):
                    self.tree.set(iid, col, record[k])

    def onDel(self):
        iid = self.tree.focus()
        if iid: self.tree.delete(iid)

    def setValue(self, value):
        lista = self.tree.get_children('')
        self.tree.delete(*lista)
        if value == '':return
        maxCol = len(self.columnsId) - 1
        if self.isTree: maxCol += 3
        bDatos = [map(lambda x: x.strip(),record.split(',', maxCol)) for record in value.split('|')]
        parent, iid, text = '', None, ''
        for record in bDatos:
            if self.isTree:
                parent, iid, text = record[:3]
                record = record[3:]
            self.tree.insert(parent, 'end', iid=iid, text=text, values=record, open=True)

    def getValue(self):
        stack = list(self.tree.get_children('')[::-1])
        bDatos = []
        while stack:
            iid = stack.pop()
            iidValues = []
            if self.isTree:
                iidValues = [self.tree.parent(iid),iid, self.tree.item(iid, 'text')]
            iidValues = iidValues + list(self.tree.item(iid, 'values'))
            iidValStr = ','.join(iidValues)
            bDatos.append(iidValStr)
            children = self.tree.get_children(iid)
            if children:
                stack.extend(list(children)[::-1])
        return '|'.join(bDatos)

class settSlider(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        valRange = map(int,options.get('range').split(','))
        scale = tk.Scale(self, variable = self.value, showvalue = 0, from_ = valRange[0], to = valRange[-1], orient = tk.HORIZONTAL)
        scale.pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        if len(valRange) == 3: scale.configure(resolution = valRange[1])
        tk.Entry(self, textvariable = self.value).pack(side = tk.RIGHT, fill = tk.X)

class settNumber(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        # valid percent substitutions (from the Tk entry man page)
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        func = self.validateNumber
        vcmd = (self.register(func),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = entry = tk.Entry(self, name = self.id, textvariable = self.value, validate = 'key', validatecommand = vcmd)
        entry.pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        self.setValue(self.default)

    def validateNumber(self, d, i, P, s, S, v, V, W):
        return S.isdigit()

    def setValue(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        pass

class settText(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        self.name = wdgName
        baseWidget.__init__(self, master, name = wdgName, id = options.get('id', ''))
        self.setGUI(options)

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.value = tk.StringVar()
        self.default = options.get('default', '')
        self.setValue(self.default)
        if options.get('id'):
            self.id = options.get('id').lower().replace('.', '__')
            tk.Entry(self, name = self.id, textvariable = self.value ).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        else:
            tk.Label(self, textvariable=self.value).pack(side=tk.RIGHT, fill=tk.X, expand=1)


    def setValue(self, value):
        if value == None:
            self.value.set('')
        else:
            self.value.set(value)

    def getValue(self):
        return self.value.get() if self.value.get() != '' else ''

class settBool(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, name=wdgName, id=options.get('id', ''))
        if options.has_key('group'):
            groupName = options['group']
            self.value = self.form.getGroupVar(groupName)
        else:
            self.setVarType('boolean')
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = id = options.get('id').lower()
        self.default = options.get('default') == 'true'
        if options.has_key('group'):
            value_on = id
            if self.default: self.setValue(id)
        else:
            value_on = True
            self.setValue(self.default)
        chkbtn = tk.Checkbutton(self, name=self.id, variable=self.value, onvalue=value_on, anchor=tk.E)
        chkbtn.pack(side = tk.RIGHT, fill = tk.X, expand = 1)

    def isValueSetToDefault(self):
        return self.getValue() == self.default

    def setValue(self, value):
        self.value.set(value)

    def getValue(self):
        value = self.value.get()
        if isinstance(value, basestring):
            value = (value == self.id)
        return value

class settAction(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        if options.get('id'): self.id = options.get('id').lower()
        self.value = options.get('default')
        tk.Button(self, name=self.id, text=options.get('label'), command=self.onClick).pack(side=tk.RIGHT, fill=tk.X,
                                                                                            expand=1)

    def onClick(self):
        pass

    def isValueSetToDefault(self):
        return True

    def setValue(self, value):
        pass

    def getValue(self):
        return None

    def setListener(self, function):
        pass

    def callListener(self, *args):
        pass

class settSep(tk.Frame):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower().lower()
        tk.Frame.__init__(self, master, name = wdgName)
        self.pack(side = tk.TOP, fill = tk.X, expand = 1)
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        if options.get('type', None) == 'lsep': tk.Label(self, text = options.get('label')).pack(side = tk.LEFT)
        if not options.has_key('noline'):
            color = options.get('color', 'red')
            tk.Frame(self, relief=tk.RIDGE, height=2, bg=color).pack(side = tk.RIGHT, fill = tk.X, expand = 1)

    def getSettingPair(self):
        return (None, None)

    def isValueSetToDefault(self):
        return True

    def setValue(self, value):
        pass

    def getValue(self):
        return None

    def setListener(self, function):
        pass

class settContainer(tk.LabelFrame):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower().replace('.', '_')
        packSide = options.get('side', 'top')
        self.side = dict(top=tk.TOP, bottom=tk.BOTTOM, left=tk.LEFT, right=tk.RIGHT).get(packSide, tk.TOP)
        id = options.get('id', wdgName).lower()
        if id != wdgName:
            self.id = id
        tk.LabelFrame.__init__(self, master, name=id, text=options.get('label'))
        if isinstance(master, settContainer) or isinstance(master, settScrolledContainer):
            packSide = master.side
            self.path = master.path + '.' + id
            self.form = master.form
        else:
            packSide = tk.TOP
            self.path = id
            self.form = master
        self.pack(side=packSide, fill=tk.X, expand=1)
        self.name = wdgName

class settScrolledContainer(tk.LabelFrame):

    def __init__(self, master, **options):
        wdgName = options.get('name').lower().replace('.', '_')
        packSide = options.get('side', 'top')
        self.side = dict(top=tk.TOP, bottom=tk.BOTTOM, left=tk.LEFT, right=tk.RIGHT).get(packSide, tk.TOP)
        id = options.get('id', wdgName).lower()
        if id != wdgName:
            self.id = id
        tk.LabelFrame.__init__(self, master, name=id, text=options.get('label'))
        if isinstance(master, settScrolledContainer) or isinstance(master, settContainer):
            packSide = master.side
            self.path = master.path + '.' + id
            self.form = master.form
        else:
            packSide = tk.TOP
            self.path = id
            self.form = master
        self.pack(side=packSide, fill=tk.X, expand=1)
        self.name = wdgName

        self.vsb = tk.Scrollbar(self, orient="vertical", )
        self.vsb.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self, name="canvas", borderwidth=0, background="SystemButtonFace")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.configure(command=self.canvas.yview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.innerframe = settContainer(self, name="innerframe")
        self.innerframeId = self.canvas.create_window((0, 0),
                                                      window=self.innerframe,
                                                      anchor="nw",
                                                      tags="innerframe")


        self.canvas.bind("<Configure>", self.OnCanvasConfigure)
        self.innerframe.bind("<Configure>", self.OnInnerFrameConfigure)

    def OnCanvasConfigure(self, event):
        if self.innerframe.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.innerframeId, width=self.canvas.winfo_width())

    def OnInnerFrameConfigure(self, event):
        size = (self.innerframe.winfo_reqwidth(), self.innerframe.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.innerframe.winfo_reqwidth() != self.canvas.winfo_width():
            width = self.innerframe.winfo_reqwidth()
            self.canvas.config(width=width)

class AppSettingDialog(tk.Toplevel):
    def __init__(self, master, xmlSettingFile, isFile = True, settings = None, title = None, dheight = None, dwidth = None):
        tk.Toplevel.__init__(self, master)
        self.resizable(False, False)
        self.transient(master)
        if title: self.title(title)
        self.parent = master
        body = tk.Frame(self, bg = 'grey')
        if dheight:
            body.configure(height=dheight)
        if dwidth:
            body.configure(width=dwidth)
        body.pack(padx=5, pady=5)
        # body.pack_propagate(0)
        self.flag = 0
        self.settings = settings or {}
        self.allSettings = None
        self.result = dict(self.settings)
        self.applySelected = False
        if isFile:
            self.root = ET.parse(xmlSettingFile).getroot()
        else:
            self.root = ET.fromstring(xmlSettingFile)
        self.initial_focus = self.setGUI(body)

        self.grab_set()
        if not self.initial_focus: self.initial_focus = self
        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.geometry("+%d+%d"%(master.winfo_rootx()+50,
                                master.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    def getSettings(self):
        return self.settings

    def Close(self):
        self.destroy()

    def setGUI(self, master):
        topPane = tk.Frame(master)
        topPane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        topPane.grid_propagate(0)
        self.topPane = topPane

        bottomPane = tk.Frame(master, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.TOP, fill = tk.X)
        for label in ['Apply', 'Cancel']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, command = partial(self.onAction, label))
            boton.pack(side = tk.RIGHT)

        self.setFrameFromXML()
        self.rightPane = None
        self.selOption(0)
        self.rightPane.pack(side = tk.TOP, fill = tk.BOTH)

        return bottomPane.children['apply']
        
    def onAction(self, action):
        self.applySelected = False
        if action == 'Apply':
            changedSettings = self.rightPane.getChangeSettings(self.settings)
            reset = changedSettings.pop('reset')
            for key in reset: self.settings.pop(key)
            self.settings.update(changedSettings)
            # self.applySelected = cmp(self.settings, self.result) != 0
            self.applySelected = reset + changedSettings.keys()
            self.result = dict(self.settings)
            self.allSettings = self.rightPane.getAllSettings(keyfunc = lambda x: int(x.name))
        self.Close()
        
        
            
    def setFrameFromXML(self):
        root = self.root
        self.intVar = tk.IntVar()
        categories = root.findall('category')
        if len(categories) <= 1: return
        self.leftPane = tk.Frame(self.topPane, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        self.leftPane.pack(side = tk.LEFT, fill = tk.Y)
        for k, elem in enumerate(categories):
            boton = tk.Radiobutton(self.leftPane, text = elem.get('label'), value = k, variable = self.intVar, command = partial(self.selOption,k), indicatoron = 0)
            boton.pack(side = tk.TOP, fill = tk.X)
        
    def selOption(self, ene):
        self.intVar.set(ene)
        if self.rightPane:
            changedSettings = self.rightPane.getChangeSettings(self.settings)
            reset = changedSettings.pop('reset')
            for key in reset: self.settings.pop(key)
            self.settings.update(changedSettings)
            self.rightPane.forget()
        selPane = self.root.findall('category')[ene]
        self.rightPane = scrolledFrame(self.topPane, self.settings, selPane)
        self.rightPane.pack(side = tk.TOP, fill = tk.BOTH)

class TreeDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, title=None, xmlFile=None, isFile=False, settings=None):
        import xmlFileWrapper
        self.settings = settings = settings or {}
        self.ads = xmlFileWrapper.xmlFileWrapper(xmlFile, isFile=isFile, nonDefaultValues=settings)
        tkSimpleDialog.Dialog.__init__(self, master, title)

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        selPanel = self.ads.getActivePane()
        self.form = form = formFrame(master, {}, selPanel)
        form.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        wdgId = sorted(form.nameToId.keys(), key=int)[0]
        wdgId = form.nameToId[wdgId]
        widget = getattr(self.form, wdgId)
        return widget

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        settings = self.settings
        changedSettings = self.form.getChangeSettings(settings)
        reset = changedSettings.pop('reset')
        for key in reset: settings.pop(key)
        settings.update(changedSettings)
        self.result = dict(settings)
        allwidgets = self.form.getWidgets()
        allwidgets.sort(key=operator.attrgetter('id'))
        allSettings = [widget.getSettingPair(tId=True) for widget in allwidgets]

        self.allSettings = allSettings
        self.cancel()
        pass

    def geometry(self, posStr):
        width, height = 290, 220
        posx = (self.winfo_screenwidth() - width) / 2
        posy = (self.winfo_screenheight() - height) / 2
        posStr = "+%d+%d" % (posx, posy)
        tkSimpleDialog.Dialog.geometry(self, posStr)


def builtAddonXmlFile(noDefaultSettings):
    root = ET.fromstring(adonxmldesc)
    addonXml = processTemplate(root)
    return addonXml


def getAddonXmlFile(xmlTemplate, settings):
    with open(xmlTemplate, 'r') as f:
        xmlTemplate = f.read()
    regexPatterns = ['"(.+?)"', '>([^<\W]+)<']       # [attribute, value]
    for regexPattern in regexPatterns:
        pos = 0
        reg = re.compile(regexPattern)
        while True:
            match = reg.search(xmlTemplate, pos)
            if not match: break
            key = match.group(1)                  #reemplazar verdadero codigo
            if settings.has_key(key):
                posINI = match.start(0) + 1
                posFIN = match.end(0) - 1
                value = settings[key]
                xmlTemplate = xmlTemplate[:posINI] + value + xmlTemplate[posFIN:]
                pos = posINI + len(value) + 1
            else:
                pos = match.end(0)
                
    # Sesion requires
    regexPattern = "<requires>(.+?)\s*</requires>"
    pos = 0
    reg = re.compile(regexPattern, re.DOTALL)
    match = reg.search(xmlTemplate, pos)
    posINI = match.start(1)
    posFIN = match.end(1)
    template = match.group(1)
    lista = [elem.split(',') for elem in settings['addon_requires'].split('|')]

    for k, elem in enumerate(lista):
        lista[k] = elem + (3 - len(elem))*['false']
        lista[k] = template.format(*lista[k]).replace('optional="false"','')
    template = ''.join(lista)
    xmlTemplate = xmlTemplate[:posINI] + template + xmlTemplate[posFIN:]
    
    # Sesion provides
    attIds = ['addon_video', 'addon_music', 'addon_picture', 'addon_program']
    attlabel = ['video', 'music', 'picture', 'program']
    template = ''
    for k, attId in enumerate(attIds):
        if settings.get(attId) == 'true':
            template += attlabel[k] + ' '
    regexPattern = "<provides>(.+?)</provides>"
    pos = 0
    reg = re.compile(regexPattern, re.DOTALL)
    match = reg.search(xmlTemplate, pos)
    posINI = match.start(1)
    posFIN = match.end(1)
    xmlTemplate = xmlTemplate[:posINI] + template.strip() + xmlTemplate[posFIN:]
    return xmlTemplate
    
def getScriptSettings(xmlSettingFile, settings):
    root = ET.parse(xmlSettingFile).getroot()
    for elem in root.iter('setting'):
        if elem.attrib.has_key('default'):
            key = elem.get('id')
            if settings.has_key(key): continue
            value = elem.get('default')
            settings[key] = value
            print key, '=', value
    return settings

def exportAddon(xmlAddonStructure, settings, calcFiles, afile = None):
    from xbmc import translatePath
    def verifyDestDir(dstFile,afile):
        if afile == None:
            dstDirectory, dstName = os.path.split(dstFile)
            if not os.path.exists(dstDirectory):
                os.makedirs(dstDirectory)
        
    def calcStringFiles(srcFile, dstFile, calcFiles, afile = None):
        verifyDestDir(dstFile, afile)
        srcString = calcFiles[srcFile]
        if not srcString: return
        if afile == None:
            with open(dstFile,'w') as wfile:
                wfile.write(srcString)
        else:
            afile.writestr(dstFile, srcString)
            
    def copySrcFile(srcFile, dstFile, afile = None):
        verifyDestDir(dstFile, afile)
        if afile == None:
            shutil.copyfile(srcFile, dstFile)
        else:
            afile.write(srcFile, dstFile)
            
    root = ET.parse(xmlAddonStructure).getroot()
    lastDirectory = ''
    for elem in root.iter():
        if elem.tag == 'structure':
            path = elem.get('path')
            path = settings[path]
            if not afile:
                baseDirectory = translatePath('special://home/addons')                
                baseDirectory = os.path.join(baseDirectory, path)
                if os.path.exists(baseDirectory):
                    if tkMessageBox.askokcancel('Export addon', 'El directorio propuesto ya existe, desea sobreescribirlo'):
                        try:
                            shutil.rmtree(baseDirectory, ignore_errors = True)
                        except:
                            tkMessageBox.showerror('Error', 'Directory acces dennied')
                            return
            else:
                afile = zipfile.ZipFile(addonzip, 'w')
                baseDirectory = path 
            lastDirectory = os.path.normpath(baseDirectory)
        elif elem.tag == 'folder':
            nameId = elem.get('id')
            path = elem.get('path')
            if not path: continue
            if elem.get('optional') == 'false' or (settings.has_key(nameId) and not elem.attrib.has_key('name')):
                path = os.path.join(baseDirectory, path)
                lastDirectory = os.path.normpath(path)
            elif settings.has_key(nameId) and elem.attrib.has_key('name'):
                name = elem.get('name')
                if name in settings[nameId]:
                    resourceFiles = [kElem.split(',') for kElem in settings[nameId].split('|')]
                    path = os.path.join(baseDirectory, path)
                    for ka in resourceFiles:
                        if name not in ','.join(ka): continue
                        srcName = ka[0]
                        dstName = os.path.normpath(os.path.join(path, srcName))
                        copySrcFile(srcName, dstName, afile)
            else:
                continue
        elif elem.tag == 'file':
            nameId = elem.get('id')
            if elem.get('optional') == 'false':
                srcName = settings.get(nameId, None) or elem.get('name')
                dstName = os.path.join(lastDirectory, srcName)
                calcStringFiles(srcName, dstName, calcFiles, afile)
            else:
                if settings.has_key(nameId):
                    srcName = settings[nameId]
                    if not os.path.exists(srcName):continue
                    dstName = elem.get('name')
                    dstName = os.path.join(lastDirectory, dstName)
                    copySrcFile(srcName, dstName, afile)
                else:
                    continue
    if afile: afile.close()    


xmlAddonFile = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="addon_id" name="addon_name" version="addon_version" provider-name="addon_provider">
  <requires>
    <import addon="{0}" version="{1}" optional="{2}"/>
  </requires>
  <extension point="xbmc.python.pluginsource" library="addon_module">
    <provides>addon_provides</provides>
  </extension>
  <extension point="xbmc.addon.metadata">
    <summary lang="en">addon_summary</summary>
    <description lang="en">addon_description</description>
    <disclaimer lang="en">addon_disclaimer</disclaimer>
    <language>addon_language</language>
    <platform>addon_platform</platform>
    <license>addon_license</license>
    <forum>addon_forum</forum>
    <website>addon_website</website>
    <email>addon_email</email>
    <source>addon_source</source>
  </extension>
</addon>
"""

xmlAddonStructure = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<structure path="addon_id">
    <folder id="addon_id" optional="false" path="">
        <file id="addon_module" optional="false" />
        <file id="addon_xml" name="addon.xml" optional="false" />
        <file id="addon_icon" name="icon.png" optional="true"  />
        <file id="addon_fanart" name="fanart.jpg" optional="true" />
        <file id="addon_changelog" name="changelog.txt" optional="true" />
        <file id="addon_license" name="licence.txt" optional="true" />
        <folder id="addon_resources" optional="true" path="resources">
            <file id="addon_settings" optional="true" />
            <folder id="addon_resources" name="language" optional="true" path="resources/language" />
            <folder id="addon_resources" name="lib" optional="true" path="resources/lib" />
            <folder id="addon_resources" name="data" optional="true" path="resources/data" />
            <folder id="addon_resources" name="media" optional="true" path="resources/media" />
        </folder>
    </folder>
</structure>
"""
xmlWidgetsAvailable = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<settings>
  <category label="Widgets types">
    <setting type="sep" label ="Type sep:    "/>
    <setting type="lsep" label ="Type lsep:    "/>
    <setting id="addon_text" type="text" label="Type text:   " default="xbmcIDEdefault"/>
    <setting id="addon_optionlst" type="optionlst" default="xbmc.python,2.1.0,|script.module.urlresolver,2.4.0," label="Type optionlst" columnsheadings = "Description, Version, Optional" />
    <setting id="addon_number" type="number" label ="type number" default="5"/>
    <setting id="addon_ipaddress" type="ipaddress" label ="type ipaddress" default="134"/>
    <setting id="addon_slider" type="slider" label ="type slider" range="10,50" default="20"/>
    <setting id="addon_bool" type="bool" label ="type bool" default="true"/>
    <setting id="addon_enum" type="enum" label="Type enum :   " default="5" values="0|1|2|3|4|5|6|7|8|9|10"/>
    <setting id="addon_labelenum" type="labelenum" label="Type labelenum :   " default="label2" lvalues="label0|label1|label2|label3|label4"/>
    <setting id="addon_dropdown" type="drpdwnlst" label="Type drpdwnlst :   " lvalues="label0|label1|label2|label3|label4" values="int0|int1|int2|int3|int4" default="int3"/>
    <setting id="addon_file" type="file" label="Type file:   " default=""/>
    <setting id="addon_audio" type="audio" label="Type audio:   " default=""/>
    <setting id="addon_video" type="video" label="Type video:   " default=""/>
    <setting id="addon_image" type="image" label="Type image:   " default=""/>
    <setting id="addon_executable" type="executable" label="Type executable:   " default=""/>
    <setting id="script_export" type="folder" label="Type Folder:   " default="c:/basura"/>
    <setting id="addon_fileenum" type="fileenum" label="Type fileenum:   " values="" mask ="*.py" hideext='false' default=""/>
    <setting id="addon_action" type="action" label="Type action:   " default=""/>
  </category>
  <category label="resources">
    <setting id="addon_fanart" type="file" label="Fanart:   " default=""/>
    <setting id="addon_license" type="file" label="License:   " default=""/>
    <setting id="addon_changelog" type="file" label="Changelog" default="" />
    <setting id="addon_resources" type="optionlst" default="basicFunc.py,resources/lib,True,basicFunc.py" label="Addon aditional resources" columnsheadings = "File, Location, Editable, Source" />
  </category>
  <category label="Directories">
  </category>
</settings>
"""
textoencius = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<settings>
    <category label="TCombobox">
        <setting id="Description" type="text" label="Description" default=""/>
        <setting id="Version" type="text" label="Version" default=""/>
        <setting id="Optional" type="text" label="Optional" default=""/>
    </category>
</settings>
"""
xmlOnePanel = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<settings>
  <category label="Widgets types">
    <setting type="scrolledcontainer" label ="Panel">
        <setting type="sep" label ="Type sep:    "/>
        <setting type="lsep" label ="Type lsep:    "/>
        <setting id="addon_text" type="text" label="Type text:   " default="xbmcIDEdefault"/>
        <setting id="addon_optionlst" type="optionlst" default="xbmc.python,2.1.0,|script.module.urlresolver,2.4.0," label="Type optionlst" columnsheadings = "Description, Version, Optional" />
        <setting id="addon_number" type="number" label ="type number" default="5"/>
        <setting id="addon_ipaddress" type="ipaddress" label ="type ipaddress" default="134"/>
        <setting id="addon_slider" type="slider" label ="type slider" range="10,50" default="20"/>
        <setting id="addon_bool" type="bool" label ="type bool" default="true"/>
        <setting id="addon_enum" type="enum" label="Type enum :   " default="5" values="0|1|2|3|4|5|6|7|8|9|10"/>
        <setting id="addon_labelenum" type="labelenum" label="Type labelenum :   " default="label2" lvalues="label0|label1|label2|label3|label4"/>
        <setting id="addon_dropdown" type="drpdwnlst" label="Type drpdwnlst :   " lvalues="label0|label1|label2|label3|label4" values="int0|int1|int2|int3|int4" default="int3"/>
        <setting id="addon_file" type="file" label="Type file:   " default=""/>
        <setting id="addon_audio" type="audio" label="Type audio:   " default=""/>
        <setting id="addon_video" type="video" label="Type video:   " default=""/>
        <setting id="addon_image" type="image" label="Type image:   " default=""/>
        <setting id="addon_executable" type="executable" label="Type executable:   " default=""/>
        <setting id="script_export" type="folder" label="Type Folder:   " default="c:/basura"/>
        <setting id="addon_fileenum" type="fileenum" label="Type fileenum:   " values="" mask ="*.py" hideext='false' default=""/>
        <setting id="addon_action" type="action" label="Type action:   " default=""/>
    </setting>
  </category>
</settings>
"""

#    

    
if __name__ == "__main__":


    fileObject = StringIO.StringIO(xmlOnePanel)
    Root = tk.Tk()
    Root.withdraw()
    test = TreeDialog(Root, 'Prueba Dialog', textoencius, isFile=False)
    Root.wait_window(test)


    # theSettings = AppSettingDialog(Root, xmlOnePanel, isFile = False, title = 'Test Window Case')
    # print theSettings.result
#     totalSettings = getScriptSettings(xmlSettingFile, theSettings.result)
#     strFiles = {}
#     strFiles['addon.xml'] = getAddonXmlFile(xmlAddonFile, totalSettings)
#     strFiles['default.py'] = tube8py  
#     print strFiles['addon.xml']
#     exportAddon(xmlAddonStructure, totalSettings, strFiles, afile = 'theFirsAddon.zip')
#     xmlFile = getAddonXmlFile(xmlAddonFile, totalSettings)    
#     print 'xmlFile *****************************\n', xmlFile

#     xmlRoot = ET.parse(fileObject).getroot()
#     selPane = xmlRoot.findall('category')[1]
#     scrollPane = scrolledFrame(Root, {}, selPane)
#     scrollPane.pack(side = tk.TOP, fill = tk.BOTH)


    # lista = myScrolledList(Root)
    # lista.pack()

    # Root.mainloop()



