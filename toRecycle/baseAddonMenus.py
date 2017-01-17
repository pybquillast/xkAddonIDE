'''
Created on 15/05/2014

@author: Alex Montes Barrios
'''
import os
import sys
import xbmc, xbmcgui, xbmcplugin
import urlparse
import urllib
import xml.dom.minidom as minidom


def build_url(query):
    urlprefix = query.get('urlprefix', None)
    if urlprefix: return urlprefix
    return base_url + '?' + urllib.urlencode(query)

def getAvailableXbmcAddons():
    pathDir = xbmc.translatePath('special://home/addons')
    addons = [addon for addon in os.listdir(pathDir) if addon.startswith('plugin.video')]
    addonsAttr = {}
    for addonDir in addons:
        addonXmlFile = os.path.join(pathDir, addonDir, 'addon.xml')
        with open(addonXmlFile, 'r') as xmlFile:
            xmlContent = xmlFile.read()
        
        xmlDom = minidom.parseString(xmlContent)
        heading = xmlDom.getElementsByTagName('addon')
        heading = dict(heading[0].attributes.items())
        addonID = heading['id']
        
        body = xmlDom.getElementsByTagName('extension')
        body = dict(body[0].attributes.items())
        
        heading.update(body)
        addonsAttr[addonID] = heading
    return addonsAttr

def makeXbmcMenu(menuContent):
    for elem in menuContent:
        urlTags, parameters, addonInfo = elem[0], elem[1], elem[2]
        url = build_url(urlTags)
        isFolder = parameters.pop('isFolder')
        if parameters.get('iconImage', None) == None:
            parameters['iconImage'] = 'defaultFolder.png' if isFolder else 'DefaultVideo.png' 
        li = xbmcgui.ListItem(**parameters)
        li.setProperty('IsPlayable', 'false' if isFolder else 'true')
        if addonInfo:
            li.setInfo(**addonInfo)
            li.addContextMenuItems([('Video Information', 'XBMC.Action(Info)')]) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(addon_handle)

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

menu = args.get('menu', None)
if menu is None:
    xbmcAddons = getAvailableXbmcAddons()
    xbmcAddons = [(xbmcAddons[key]['name'], key) for key in xbmcAddons.keys()]
    xbmcAddons.sort()
    menuContent = []
    for name, key in xbmcAddons:
        urlTags = {'urlprefix': 'plugin://' + key + '/?'}
        parameters= {'label':name, 'isFolder':True}
        imgFile = xbmc.translatePath('special://home/addons/' + key + '/icon.png')
        if os.path.exists(imgFile): parameters['thumbnailImage'] = imgFile
        imgFile = xbmc.translatePath('special://home/addons/' + key + '/fanart.jpg')
        if os.path.exists(imgFile): parameters['iconImage'] = imgFile
        addonInfo = None
        menuContent.append([urlTags, parameters, addonInfo])
    menuContent.append([{'menu':'listDir', 'baseDir':'\\\\Alexcasa\\Public\\Videos\\Sample Videos'}, {'label':'_Peliculas', 'isFolder':True}, False])
    makeXbmcMenu(menuContent)
elif menu[0] == 'listDir':
    baseDir = args.get('baseDir')[0]
    dirContent = os.listdir(baseDir)
    dirContent.sort(key = lambda elem: '1' + elem if os.path.isdir(baseDir + '\\' + elem) else '2' + elem, reverse = True)
    menuContent = []
    while os.path.isdir(baseDir + '\\' + dirContent[-1]):
        elemDir = dirContent.pop()
        dirName = baseDir + '\\' + elemDir + '\\'
        urlTags = {'menu':'listDir', 'baseDir':dirName}
        parameters= {'label':elemDir, 'isFolder':True}
        addonInfo = None
        menuContent.append([urlTags, parameters, addonInfo])
    while dirContent:
        elemDir = dirContent.pop()
        if os.path.splitext(elemDir)[1] in ['.avi', '.mkv', '.mp4', '.wmv']:
            filePath = baseDir + '\\' + elemDir
            urlTags = {'menu':'mediaFile', 'filePath':filePath}
            parameters= {'label':elemDir, 'isFolder':False}
            addonInfo = None
            menuContent.append([urlTags, parameters, addonInfo])
    makeXbmcMenu(menuContent)
elif menu[0] == 'mediaFile':
    filePath = args.get('filePath')[0]
    os.startfile(filePath)
        
    
