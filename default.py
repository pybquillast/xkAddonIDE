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

def rootmenu():      # Modified code
    menuContent = []
    args["url"] = ["https://seriesenlinea.net/serie/sr-avila/"]
    menuContent.extend(links())
    return menuContent


def links():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("links", dir=_data)
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

def media():      # Modified code
    url = args.get("url")[0]
    compflags, regexp = None, r'(?#<div id="embed1" iframe.src=url>)'
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags )
    url = subMenus[0]["url"]
    compflags, regexp = None, r"(?#<source res='720p' src=url>)"
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags )
    url = subMenus[0]["url"]
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
