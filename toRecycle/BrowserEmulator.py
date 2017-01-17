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

ese = 'este es  comentario sin tilde al final
esta frse no se colorea verde

ese = "este tiene la ultima tilde con escape \' y sigue el comentario
ese = "esta tiene  tilde con escape \' pero tilde al final "   2345566


"""

class OptionWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
#         self.protocol('WM_DELETE_WINDOW', self.Close)
        self.flag = 0
        self.setGUI(master)
#
    def Close(self):
        self.destroy()
"""
    234
    234.45
    2.56.487.980  alex
    
#esto

    def                          setGUI(self, master):
        topPane = tk.Frame(master, height = 500, width = 500)
        topPane.pack(side = tk.TOP)
        topPane.pack_propagate(0)
        leftPane = tk.Frame(topPane, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        opNames = ['Addon', 'Dependencies', 'Metadata']
        for ene in range(len(opNames)):
            boton = tk.Button(leftPane, text = opNames[ene], anchor = tk.W, command = partial(self.selOption, ene))
            boton.pack(side = tk.TOP, fill = tk.X)
        leftPane.pack(side = tk.LEFT, fill = tk.Y)
        self.rightPane = tk.Frame(topPane, padx = 3, pady = 3)
        self.rightPane.pack(side = tk.TOP, fill = tk.BOTH)
        self.topPane = topPane
        self.selOption(0)
        bottomPane = tk.Frame(master, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.TOP, fill = tk.X)
        for label in ['OK', 'Cancel']:
            boton = tk.Button(bottomPane, text = label)
            boton.pack(side = tk.RIGHT)
        
   '''         
    def selOption(self, ene):
        self.rightPane.forget()
        self.rightPane = tk.Frame(self.topPane, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3, height = 300, width = 400)
        self.rightPane.grid_propagate(0)
        self.rightPane.pack(side = tk.TOP)
        if ene == 0: return self.addon(self.rightPane)
        if ene == 1: return self.dependencies(self.rightPane)
        if ene == 2: return self.metadata(self.rightPane)
        
        if self.flag:
            for label in ['izquierda', 'derecha']:
                boton = tk.Button(self.rightPane, text = label + str(ene))
                boton.pack(side = tk.LEFT)
        else:
            for label in ['ariba', 'abajo']:
                boton = tk.Button(self.rightPane, text = label + str(ene))
                boton.pack(side = tk.TOP)
        self.flag = 1 - self.flag
            
    def metadata(self, master):
        topPane =  tk.Frame(master)
        topPane.pack(side = tk.TOP, padx = 3, pady = 3)
        
        tk.Label(topPane, text = 'Summary:').grid(row = 0, column = 0, sticky = tk.W)
        tk.Entry(topPane).grid(row = 1, column = 0, sticky = tk.W, rowspan = 3)
        tk.Label(topPane, text = 'Description:').grid(row = 4, column = 0, sticky = tk.W)
        tk.Entry(topPane).grid(row = 5, column = 0, sticky = tk.W, rowspan = 6)
        
        bottomPane = tk.Frame(master)
        bottomPane.pack(side = tk.TOP, padx = 3, pady = 3)
       
        rightPane = tk.Frame(bottomPane)
        rightPane.pack(side = tk.RIGHT)
        for k, elem in enumerate(['Forum', 'Website', 'Email', 'source']):
            tk.Label(rightPane, text = elem).grid(row = k, column = 0, sticky = tk.W)
            tk.Entry(rightPane).grid(row = k, column = 2)
            
        leftPane = tk.Frame(bottomPane)
        leftPane.pack(side = tk.LEFT)
        for k, elem in enumerate(['Disclaimer', 'Language', 'Platform', 'License']):
            tk.Label(leftPane, text = elem).grid(row = k, column = 0, sticky = tk.W)
            tk.Entry(leftPane).grid(row = k, column = 2)
            
        slackPane = tk.Frame(master)
        slackPane.pack(side = tk.TOP, padx = 3, pady = 3, fill = tk.BOTH, expand = 1)
            

    def addon(self, master):
        topPane = tk.Frame(master)
        topPane.pack(side = tk.TOP, padx = 3, pady = 3)
       
        rightPane = tk.Frame(topPane)
        rightPane.pack(side = tk.RIGHT)
        for k, elem in enumerate(['Version', "Provider's name"]):
            tk.Label(rightPane, text = elem).grid(row = k, column = 0, sticky = tk.W)
            tk.Entry(rightPane).grid(row = k, column = 2)
            
        leftPane = tk.Frame(topPane)
        leftPane.pack(side = tk.LEFT)
        for k, elem in enumerate(['ID', 'Name']):
            tk.Label(leftPane, text = elem).grid(row = k, column = 0, sticky = tk.W)
            tk.Entry(leftPane).grid(row = k, column = 2)
        
        middlePane = tk.Frame(master)
        middlePane.pack(side = tk.TOP, padx = 3, pady = 3)
        tk.Label(middlePane, text = 'Provides').grid(row = 0, column = 0, sticky = tk.W)
        for k, elem in enumerate(['Video', "Music", 'Picture']):
            tk.Checkbutton(middlePane, text = elem).grid(row = 0, column = 1 + k, sticky = tk.W)
        tk.Label(middlePane, text = 'Initial module').grid(row = 2, column = 0, columnspan = 2, sticky = tk.W)
        tk.Entry(middlePane).grid(row = 2, column = 3, columnspan = 2)
        for k, elem in enumerate(['Icon file', "Fanart file"]):
            tk.Label(middlePane, text = elem).grid(row = 3 + k, column = 0, columnspan = 2, sticky = tk.W)
            tk.Entry(middlePane).grid(row = 3 + k, column = 3, columnspan = 2)
            tk.Button(middlePane, text = 'Browse').grid(row = 3 + k, column = 5)
        bottomPane = tk.Frame(master, relief = tk.GROOVE, borderwidth = 2, padx = 3, pady = 3)
        bottomPane.pack(side = tk.TOP, padx = 3, pady = 3)
        tk.Label(bottomPane, text = 'Requires').grid(row = 0, column = 0, sticky = tk.W)
        tk.Listbox(bottomPane, selectmode = 'SINGLE', width = 50, relief=tk.SUNKEN).grid(row = 1, column = 0, rowspan = 5,columnspan = 5)
        tk.Button(bottomPane, text = 'Add').grid(row = 7, column = 0, sticky = tk.W, padx = 3, pady = 3)
        tk.Button(bottomPane, text = 'Del').grid(row = 7, column = 4, sticky = tk.E, padx = 3, pady = 3)
        slackPane = tk.Frame(master)
        slackPane.pack(side = tk.TOP, padx = 3, pady = 3, fill = tk.BOTH, expand = 1)

    def dependencies(self, master):
        bottomPane = tk.Frame(master, relief = tk.GROOVE, borderwidth = 2, padx = 3, pady = 3)
        bottomPane.pack(side = tk.TOP, padx = 3, pady = 3)
        tk.Label(bottomPane, text = 'Modules needed').grid(row = 0, column = 0, sticky = tk.W)
        tk.Listbox(bottomPane, selectmode = 'SINGLE', width = 50, relief=tk.SUNKEN).grid(row = 1, column = 0, rowspan = 5,columnspan = 5)
        tk.Button(bottomPane, text = 'Add').grid(row = 7, column = 0, sticky = tk.W, padx = 3, pady = 3)
        tk.Button(bottomPane, text = 'Del').grid(row = 7, column = 4, sticky = tk.E, padx = 3, pady = 3)
        slackPane = tk.Frame(master)
        slackPane.pack(side = tk.TOP, padx = 3, pady = 3, fill = tk.BOTH, expand = 1)

adonxmldesc = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<tag id ="addon">
    <attrib id="id" value="script.hello.world" />
    <attrib id="name" value="Hello World" />
    <attrib id="version" value="0.0.1" />
    <attrib id="provider-name" value="Dev1, Dev2" />
    <tag id="requires">
        <tag id="import">
            <attrib id="addon" value="xbmc.python" />
            <attrib id="version" value="2.1.0" />
        </tag>
        <tag id="import">
            <attrib id="addon" value="script.module.elementtree" />
            <attrib id="version" value="1.2.7" />
        </tag>
        <tag id="import">
            <attrib id="addon" value="script.module.simplejson" />
            <attrib id="version" value="2.0.10" />
            <attrib id="optional" value="False" />        
        </tag>
    </tag>
    <tag id = "extension">
        <attrib id="point" value="xbmc.python.pluginsource" />
        <attrib id="library" value="default" />
        <tag id = "provides">
            audio video
        </tag>
    </tag>
    <tag id = "extension">
        <attrib id="point" value="xbmc.addon.metadata" />
        <tag id = "summary">
            <attrib id="lang" value="en" />
            Hello World script provides some basic examples on how to create your first script
        </tag>
        <tag id = "description">
            <attrib id="lang" value="en" />
            Hello World script provides some basic examples on how to create your first script
            and hopefully will increase the number of users to start crating their own addons.
        </tag>
        <tag id = "platform">
            All
        </tag>
        <tag id = "license">
            GENERAL PUBLIC LICENSE. Version  2, June 1991
        </tag>
        <tag id = "forum">
            http://www.myaddonwebsite.com/forum.php?thread=12345
        </tag>
        <tag id = "website">
            http://www.myaddonwebsite.com/
        </tag>
        <tag id = "source">
            http://github.com/someone/source/myaddon
        </tag>
        <tag id = "email">
            foo@bar.com
        </tag>
        <tag id = "disclaimer">
            Feel free to use this script. For information visit the wiki
        </tag>
    </tag>
</tag>
"""


def builtAddonXmlFile():
    root = ET.fromstring(adonxmldesc)
    addonXml = processTemplate(root)
    return addonXml

def processTemplate(node, parent = None):
    if node.tag == 'tag':
        if parent == None:
            xmlNode = ET.Element(node.attrib['id'])
        else:
            xmlNode = ET.SubElement(parent, node.attrib['id'])
        if node.text: xmlNode.text = node.text 
        for elem in node.getchildren():
            newNode = processTemplate(elem, xmlNode)
        return xmlNode
    elif node.tag == 'attrib':
        key = node.attrib['id']
        value = node.attrib['value']
        parent.attrib[key] = value
        return parent
    
def getAddonXmlFile(xmlTemplate, settings):
    regexPatterns = ['"(.+?)"', '>([^<\W]+)<']       # [attribute, value]
    for regexPattern in regexPatterns:
        pos = 0
        reg = re.compile(regexPattern)
        while True:
            match = reg.search(xmlTemplate, pos)
            if not match: break
            key = match.string                  #reemplazar verdadero codigo
            if settings.has_key(key):
                posINI = match.start(0)
                posFIN = match.end(0)
                value = settings[key]
                xmlTemplate = xmlTemplate[:posINI] + value + xmlTemplate[posFIN:]
                pos = posINI + len(value)
            else:
                pos = match.end(0)
    return xmlTemplate
    
def getScriptSettings(root, settings):    
    return settings
    
        
"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="addon_id" name="addon_name" version="addon_version" provider-name="addon_provider">
  <requires>
    <import addon="pos0" version="pos1"/>
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
 
if __name__ == "__main__":
     
    Root = tk.Tk()
#     Root.withdraw()
#     Root.resizable(0, 0)
 
#     OptionWindow(Root)
    addonxml = builtAddonXmlFile()
    tree = ET.ElementTree(addonxml)
    Root.mainloop()

'''''''''''''
    




