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
    menuContent.append([{u'url': u'http://321movies.co/film', 'menu': u'movieslist'}, {'isFolder': True, 'label': 32003}, None])
    args["url"] = ["http://321movies.co/"]
    menuContent.extend(yeargenre())
    menuContent.append([{u'url': u'http://321movies.co/anime', 'menu': u'tvshows'}, {'isFolder': True, 'label': 32004}, None])
    menuContent.append([{u'url': u'http://321movies.co/episodes', 'menu': u'newestepisodes'}, {'isFolder': True, 'label': 32006}, None])
    menuContent.append([{u'url': u'http://321movies.co/?s=supergirl', 'menu': u'search'}, {'isFolder': True, 'label': 32013}, None])
    return menuContent

def search():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("search", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'media', u'compflags': u''})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def newestepisodes():
    url = args.get("url")[0]
    footmenu = getRegexFor("newestepisodes", type="rfoot", dir=_data)
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    compflags, regexp = getRegexFor("newestepisodes", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'media'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def tvshows():
    url = args.get("url")[0]
    footmenu = getRegexFor("tvshows", type="rfoot", dir=_data)
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    compflags, regexp = getRegexFor("tvshows", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'episodes'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def episodes():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("episodes", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'media', u'compflags': u'', u'urlout': u'/anime/'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def yeargenre():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("yeargenre", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'years', u'plainnode': 1})
        paramDict.update(elem)
        paramDict["url"] = url
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def years():
    url = args.get("url")[0]
    limInf, limSup = eval(args.get("span", ["(0,0)"])[0])
    compflags, regexp = getRegexFor("years", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags, posIni = limInf, posFin = limSup)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'movieslist', u'compflags': u''})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def movieslist():
    url = args.get("url")[0]
    footmenu = getRegexFor("movieslist", type="rfoot", dir=_data)
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    compflags, regexp = getRegexFor("movieslist", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    optionMenu = {u'/anime/': u'episodes'}
    menuDef = "media"
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        menu = getMenu(elem["url"], menuDef, optionMenu)
        itemParam["isFolder"] = menu != "media"
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def media():      # Modified code
    import teleresolvers
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("media", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags )
    videoUrl = subMenus[0]["videourl"]
    url = teleresolvers.getMediaUrl(videoUrl)
    li = xbmcgui.ListItem(path = url)
    if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])
    if args.get("labeldef", None): li.setLabel(args["labeldef"][0])
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')

menu = args.get('menu', ['rootmenu'])[0]
menuFunc = globals()[menu]
menuItems = menuFunc()
if menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)    
