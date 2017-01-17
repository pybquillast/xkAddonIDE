import os, sys
import xbmcaddon
import xbmc
import xbmcplugin
import xbmcgui
import urlparse
import urllib
import re

_settings = xbmcaddon.Addon()
_path = xbmc.translatePath(_settings.getAddonInfo('path')).decode('utf-8')
_lib = os.path.join(_path, 'resources', 'lib')
_media = os.path.join(_path, 'resources', 'media')
_data = os.path.join(_path, 'resources', 'data')
sys.path.append(_lib)

EMPTYCONTENT = [[{}, {"isFolder": True, "label": ""}, None]]

import basicFunc
from basicFunc import openUrl, parseUrlContent, makeXbmcMenu, getMenu, getMenuHeaderFooter, processHeaderFooter, getRegexFor, LISTITEM_KEYS, INFOLABELS_KEYS


def rootmenu():
    menuContent = []
    menuContent.append([{'menu': u'opcion1'}, {'isFolder': True, 'label': 32004}, None])
    menuContent.append([{'menu': u'opcion2'}, {'isFolder': True, 'label': 32007}, None])
    iconList = ["tube8_icon.png", "xvideos.png"]
    for k, elem in enumerate(menuContent):
        icon = iconList[min(k, len(iconList))]
        elem[1]["iconImage"] = os.path.join(_media, icon)
    return menuContent

def opcion1():
    menuContent = []
    args["url"] = ["http://www.tube8.com"]
    menuContent.extend(Content())
    return menuContent

def opcion2():
    menuContent = []
    menuContent.append([{u'url': u'http://www.xvideos.com/?k=barranquilla', 'menu': u'srchvideos'}, {'isFolder': True, 'label': 32002}, None])
    menuContent.append([{u'url': u'http://www.xvideos.com', 'menu': u'vlist'}, {'isFolder': True, 'label': 32014}, None])
    return menuContent

def srchvideos():      # Modified code
    global args
    dlg = xbmcgui.Dialog()
    tosearch = dlg.input('Search videos with: ')
    if not tosearch: return EMPTYCONTENT
    url = 'http://www.xvideos.com/?' + urllib.urlencode(dict(k=tosearch))
    args['url'] = [url]
    args['menu'] = ['vlist']
    return vlist()





# Deleted node xvideos

def vlist():
    url = args.get("url")[0]
    headmenu = getRegexFor("vlist", type="rhead", dir=_data)
    footmenu = getRegexFor("vlist", type="rfoot", dir=_data)
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    compflags, regexp = getRegexFor("vlist", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["url", "header", "footer"]])
        paramDict.update({'menu': u'media', u'compflags': u're.DOTALL|re.IGNORECASE'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def Content():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("Content", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'listaVideos', u'compflags': u're.DOTALL|re.IGNORECASE', u'plainnode': 1})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

# Deleted node CategoryList

# Deleted node CategoryFilter

def listaVideos():
    url = args.get("url")[0]
    headmenu = getRegexFor("listaVideos", type="rhead", dir=_data)
    footmenu = getRegexFor("listaVideos", type="rfoot", dir=_data)
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    compflags, regexp = getRegexFor("listaVideos", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["url", "header", "footer"]])
        paramDict.update({u'': u'', 'menu': u'media', u'compflags': u're.DOTALL|re.IGNORECASE'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def media():      # Modified code
    url = args.get("videoUrl", None)[0]
    url, data = openUrl(url)
    compflags = re.DOTALL
    
    if url.startswith('http://www.xvideos'):
        regexp = r'_url=(?P<videoUrl>.+?)&'
        encurl = re.findall(regexp, data, compflags)[0]
        url = urllib.unquote(encurl)
        pass
    else:
        regexp = '"(?P<quality>quality_[0-9]+p)":"(?P<url>[^"]+)"'
        qualities = re.findall(regexp, data, compflags)
        encvideourl = ''
        if qualities: quality, encvideourl = qualities.pop()
        url = encvideourl.replace('\/', '/')

    li = xbmcgui.ListItem(path = url)
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle     = addon_handle, succeeded=True, listitem=li)








base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')

menu = args.get('menu', None)

menuFunc = menu[0] if menu else 'rootmenu'
menuItems = eval(menuFunc + '()')
if menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)
