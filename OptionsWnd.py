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

import StringIO

def widgetFactory(master, settings, selPane):
    enableEc = []
    for k, setting in enumerate(selPane.findall('setting')):
        setting.attrib['name'] = str(k)
        if setting.attrib.get('enable', None):
            enableEc.append((k, setting.attrib['enable']))
        if setting.get('type') in ['sep', 'lsep']:
            dummy = settSep(master, **setting.attrib)
        elif setting.get('type') == 'text':
            dummy = settText(master, **setting.attrib)
        elif setting.get('type') == 'optionlst':
            dummy = settOptionList(master, **setting.attrib)
        elif setting.get('type') in ['number', 'ipaddress'] :
            dummy = settNumber(master, **setting.attrib)
        elif setting.get('type') == 'slider':
            dummy = settSlider(master, **setting.attrib)
        elif setting.get('type') == 'bool':
            dummy = settBool(master, **setting.attrib)
        elif setting.get('type') in ['enum', 'labelenum']:
            dummy = settEnum(master, **setting.attrib)
        elif setting.get('type') == 'drpdwnlst':
            dummy = settDDList(master, **setting.attrib)
        elif setting.get('type') in ["file", "audio", "video", "image","executable"]:
            dummy = settFile(master, **setting.attrib)
        elif setting.get('type') == 'folder':
            dummy = settFolder(master, **setting.attrib)
        elif setting.get('type') == 'fileenum':
            dummy = settFileenum(master, **setting.attrib)
        elif setting.get('type') == 'action':
            dummy = settAction(master, **setting.attrib)
        try:
            key = dummy.id
        except:
            pass
        else:
            if settings and settings.has_key(key):
                dummy.setValue(settings[key])
    return enableEc


class scrolledFrame(tk.Frame):
    def __init__(self, master, settings, selPane):
        self.initDescenAscend()
        tk.Frame.__init__(self, master)
        self.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.frame.pack()
        self.populateWithSettings(settings, selPane)
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
                   
    def populateWithSettings(self, settings, selPane):
        enableEq = widgetFactory(self.frame, settings, selPane)
        self.category = selPane.get('label')
        self.registerEc(enableEq)
        self.setDependantWdgState()
        self.registerChangeListeners()
        
    def modifySettingsValues(self, settings, filterFlag = lambda widget: hasattr(widget, 'id')):
        widgets = self.widgets(filterFlag)
        map(lambda w: w.setValue(settings.get(w.id, w.default)), widgets)
            
    def registerChangeListeners(self):
        for key in self.dependents.keys():
            self.frame.children[key].setListener(self.varChange)
            
    def varChange(self, widgetName):
        interiorFrame = self.frame
        for widget in self.dependents[widgetName]:
            enableEq = self.enEquations[widget]
            calcState = self.findWidgetState(enableEq)
            theFrame = interiorFrame.children[widget]
            try:
                idKey = theFrame.id
                theFrame.children[idKey].configure(state = calcState)
            except:
                pass
            

    def setDependantWdgState(self):
        interiorFrame = self.frame
        for key in sorted(self.enEquations.keys(), key = int):
            enableEq = self.enEquations[key]
            calcState = self.findWidgetState(enableEq)
            theFrame = interiorFrame.children[key]
            try:
                idKey = theFrame.id
                theFrame.children[idKey].configure(state = calcState)
            except:
                pass
        
            
    def registerEc(self, enableEquations):
        for posWidget, enableEc in enableEquations:
            enableEc = self.getAbsEcuation(posWidget, enableEc)
            wVars = self.findVars(enableEc)
            for elem in wVars:
                self.dependents[str(elem)] = self.dependents.get(str(elem),[]) + [str(posWidget)]
            self.enEquations[str(posWidget)] = enableEc.replace('+', ' and ')
        
    def findWidgetState(self, enableEq):
        eq = lambda x,a:self.frame.children[str(x)].getValue() == a
        lt = lambda x,a:self.frame.children[str(x)].getValue() < a
        gt = lambda x,a:self.frame.children[str(x)].getValue() > a
        state = eval(enableEq) >= 1
        return tk.NORMAL if state else tk.DISABLED
        
    def initDescenAscend(self):
        self.settings = {}
        self.enEquations = {}
        self.dependents = {}        
        
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
         
        
    def getAbsEcuation(self, pos, enableEc):
        for tag in ['eq(', 'lt(', 'gt(']:
            enableEc = enableEc.replace(tag, tag + '+')
        enableEc = enableEc.replace('+-', '-').replace('!', 'not ')
        enableEc = enableEc.replace('true','True').replace('false','False').replace(',)',',None)')
        for tag in ['eq(', 'lt(', 'gt(']:
            enableEc = enableEc.replace(tag, tag + str(pos))
        return enableEc

    def getChangeSettings(self, settings):                
        interiorFrame = self.frame
        changedSettings = dict(reset = []) 
        for childName in sorted(interiorFrame.children.keys(), key = int):
            child = interiorFrame.children[childName]
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
        allWidgets = self.frame.children.values() 
        return [aWidget for aWidget in allWidgets if filterFunc(aWidget)] if filterFunc else allWidgets

    def getAllSettings(self, keyfunc = None):
        keyfunc = keyfunc or operator.attrgetter('id')
        allwidgets = self.widgets(filterFunc = lambda widget: hasattr(widget, 'id'))
        allwidgets.sort(key = keyfunc)
        return [widget.getSettingPair(tId = True) for widget in allwidgets]



class baseWidget(tk.Frame):
    def __init__(self, master, **options):
        self._id = options.pop('id')
        wdgName = options.pop('name').lower()
        if options.has_key('varType'): self.setVarType(options.pop('varType')) 
        self.default = None
        baseConf = dict(name = wdgName, bd = 1, highlightbackground='dark grey', highlightthickness = 2, highlightcolor = 'green', takefocus = 1)
        baseConf.update(options) 
        tk.Frame.__init__(self, master, **baseConf)
        self.pack(side = tk.TOP, fill = tk.X, expand = 1, ipadx = 2, ipady = 2, padx = 1, pady = 1)
        
    def setVarType(self, varType = 'string'):
        if   varType == 'int'    : self.value = tk.IntVar()
        elif varType == 'double' : self.value = tk.DoubleVar()
        elif varType == 'boolean': self.value = tk.BooleanVar()
        else: self.value = tk.StringVar()
        

    def getSettingPair(self, tId = False):
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
        wdgName = options.pop('name').lower()
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
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
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
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        tk.Button(self, name = self.id, textvariable = self.value, command = self.getFolder ).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        
    def getFolder(self):
        folder = tkFileDialog.askdirectory()
        if folder:
            self.value.set(folder)
        
class settFile(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        tk.Button(self, name = self.id, anchor = 'e', textvariable = self.value, command = self.getFile ).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        
    def getFile(self):
        fileName = tkFileDialog.askopenfilename()
        if fileName:
            self.value.set(fileName)

class settDDList(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.spBoxValues = options.get('values').split('|')
        self.lvalues = spBoxValues = options.get('lvalues').split('|')
        tk.Spinbox(self, name = self.id, textvariable = self.value, values = spBoxValues).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
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

class settEnum(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
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
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        settSep(self, name = 'label', type = 'lsep', label = options.get('label')).pack(side = tk.TOP, fill = tk.X)

        self.id = options.get('id').lower().replace('.', '__')
        self.default = options.get('default', '')
        
        uFrame = tk.Frame(self)
        uFrame.pack(side = tk.TOP, fill = tk.BOTH)

        sbar = tk.Scrollbar(uFrame)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        colHeadings = options.get('columnsheadings')
        columnsId = map(lambda x: x.strip(),colHeadings.split(','))
        tree = ttk.Treeview(uFrame, show = 'headings', columns = columnsId, displaycolumns = columnsId)
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
        
    def onAdd(self):
        newLstEntry = tkSimpleDialog.askstring('Settings', 'Enter new option vith value separarated by commas')
        if newLstEntry:
            record = map(lambda x: x.strip(),newLstEntry.split(','))
            self.tree.insert('', 'end', text='', values=record)
    
    def onEdit(self):
        iid = self.tree.focus()
        if iid:
            iidValues = []
            for col in self.columnsId:
                iidValues.append(self.tree.set(iid, col))
            iidValStr = ','.join(iidValues)
            newLstEntry = tkSimpleDialog.askstring('Edit', 'Edit record', initialvalue = iidValStr)
            if newLstEntry and iidValStr != newLstEntry:
                record = map(lambda x: x.strip(),newLstEntry.split(','))
                for k, col in enumerate(self.columnsId):
                    self.tree.set(iid, col, record[k])

    def onDel(self):
        iid = self.tree.focus()
        if iid: self.tree.delete(iid)
        
    def setValue(self, value):
        lista = self.tree.get_children('')
        self.tree.delete(*lista)
        if value == '':return
        maxCol = len(self.columnsId) - 1
        bDatos = [map(lambda x: x.strip(),record.split(',', maxCol)) for record in value.split('|')]
        for record in bDatos:
            self.tree.insert('', 'end', text='', values=record)

    def getValue(self):
        lista = self.tree.get_children('')
        bDatos = []
        for iid in lista:
            iidValues = []
            for col in self.columnsId:
                iidValues.append(self.tree.set(iid, col))
            iidValStr = ','.join(iidValues)
            bDatos.append(iidValStr)
        return '|'.join(bDatos)
        
class settSlider(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        valRange = map(int,options.get('range').split(','))
        scale = tk.Scale(self, variable = self.value, showvalue = 0, from_ = valRange[0], to = valRange[-1], orient = tk.HORIZONTAL)
        scale.pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        if len(valRange) == 3: scale.configure(resolution = valRange[1])
        tk.Entry(self, textvariable = self.value).pack(side = tk.RIGHT, fill = tk.X)

class settNumber(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'string', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
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
        wdgName = options.pop('name').lower()
        self.name = wdgName        
        baseWidget.__init__(self, master, name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower().replace('.', '__')
        self.value = tk.StringVar()
        self.default = options.get('default', '')
        self.setValue(self.default)
        tk.Entry(self, name = self.id, textvariable = self.value ).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        
    def setValue(self, value):
        if value == None:
            self.value.set('')
        else:
            self.value.set(value)
        
    def getValue(self):
        return self.value.get() if self.value.get() != '' else ''


class settBool(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        baseWidget.__init__(self, master, varType = 'boolean', name = wdgName, id = options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
        self.default = options.get('default')=='true'
        self.setValue(self.default)
        tk.Checkbutton(self, name=self.id, variable=self.value, onvalue=True, offvalue=False, anchor=tk.E).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        

class settSep(tk.Frame):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower().lower()
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


class settAction(tk.Frame):
    def __init__(self, master, **options):
        wdgName = options.pop('name').lower()
        tk.Frame.__init__(self, master, name = wdgName, bd = 1, highlightbackground = 'black')
        self.pack(side = tk.TOP, fill = tk.X, expand = 1)
        self.setGUI(options)
        self.name = wdgName
        
    def setGUI(self, options):
        tk.Label(self, text = options.get('label'), width=20, anchor=tk.NW).pack(side = tk.LEFT)
        self.id = options.get('id').lower()
        self.value = options.get('action')
        tk.Button(self, name = self.id, command = self.runScript).pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        
    def runScript(self):
        pass
        
    def getSettingPair(self):
        return (self.id, self.value)
    
    def isValueSetToDefault(self):
        return True
    
    def setValue(self, value):
        pass

    def getValue(self):
        return None
    
    def setListener(self, function):
        pass
        

class AppSettingDialog(tk.Toplevel):
    def __init__(self, master, xmlSettingFile, isFile = True, settings = None, title = None, dheight = 600, dwidth = 500):
        tk.Toplevel.__init__(self, master)
        self.resizable(False, False)
        self.transient(master)
        if title: self.title(title)
        self.parent = master
        body = tk.Frame(self, height = dheight, width = dwidth, bg = 'grey')
        body.pack(padx=5, pady=5)
        body.pack_propagate(0)
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
        topPane = tk.Frame(master, height = 500, width = 500)
        topPane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        topPane.grid_propagate(0)
        self.topPane = topPane
        self.setFrameFromXML()
        self.rightPane = None
        self.selOption(0)
        self.rightPane.pack(side = tk.TOP, fill = tk.BOTH)
        bottomPane = tk.Frame(master, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.TOP, fill = tk.X)
        for label in ['Apply', 'Cancel']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, command = partial(self.onAction, label))
            boton.pack(side = tk.RIGHT)
            
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

#    

    
if __name__ == "__main__":
    fileObject = StringIO.StringIO(xmlWidgetsAvailable)
    Root = tk.Tk()

    Root.title('PRINCIPAL')
    theSettings = AppSettingDialog(Root, fileObject, title = 'Test Window Case')
    print theSettings.result
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
        
    Root.mainloop()



